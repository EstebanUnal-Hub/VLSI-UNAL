#!/usr/bin/env python3
"""
tim_to_cir_asic.py
Convierte un .tim (GTKWave Timing Analyzer) a un .cir con fuentes PWL tipo square.
Mapeos específicos para tu chip:
 A[3:0] -> ui_in[3..0]
 B[3:0] -> ui_in[7..4]
 clk -> V_clk
 init -> V_uio_in[0]
 rst (o rst_n) -> V_rst_n
"""

import re
import sys
import math
from collections import defaultdict

# ---------- CONFIG ----------
VDD = 3.3
DEFAULT_OUT_SUFFIX = ".cir"
EPSILON_FACTOR = 1e-3   # epsilon ~ EPSILON_FACTOR * time_scale (ajustable)
MIN_EPS = 1e-12         # eps mínimo absoluto
# Mapeo lógico nombre en TIM -> (nombre fuente SPICE, nodo)
SIGNAL_MAP = {
    "clk":    ("V_clk", "clk"),
    "init":   ("V_uio_in[0]", "uio_in[0]"),
    "rst":    ("V_rst_n", "rst_n"),
    "rst_n":  ("V_rst_n", "rst_n"),
    # Los bits se generarán desde buses A[3:0] y B[3:0]
}

# Buses que queremos extraer: name, msb, lsb, base index in ui_in
BUS_MAP = {
    "A[3:0]": ("ui_in", 3, 0, 0),  # ui_in[3..0] -> V_ui_in[3..0]
    "B[3:0]": ("ui_in", 3, 0, 4),  # ui_in[7..4] -> V_ui_in[7..4] (base 4)
}

# ---------- UTIL ----------
def safe_name(s):
    return re.sub(r'[^\w]', '_', s)

def hex_to_bits(hexstr, width):
    """Convierte string hex (ej '0F' o 'F') a lista de bits [msb..lsb] de longitud width"""
    try:
        val = int(hexstr, 16)
    except ValueError:
        return [0]*width
    bits = [(val >> i) & 1 for i in range(width)]
    bits = list(reversed(bits))  # ahora msb..lsb
    if len(bits) < width:
        # pad front
        bits = [0]*(width-len(bits)) + bits
    return bits[-width:]

# ---------- PARSER TIM ----------
def parse_tim(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Time scale
    m = re.search(r'Time_Scale:\s*([0-9.Ee+\-]+)', content)
    if not m:
        time_scale = 1e-12
    else:
        time_scale = float(m.group(1))
    # time_scale meaning: the TIM times are in units of 'time_scale' seconds.
    # p.e. Time_Scale: 1.000000E-12  -> numbers like 10000.0 correspond to 10000 * time_scale seconds
    # convertirlas a segundos al multiplicar por time_scale

    # Encontrar bloques Digital_Signal y Digital_Bus
    # Hacemos un split por bloques usando lookahead para Digital_Signal / Digital_Bus
    blocks = re.split(r'(?=Digital_Signal|Digital_Bus)', content)

    digital_signals = {}
    digital_buses = {}

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block.startswith("Digital_Signal"):
            # nombre
            name_m = re.search(r'Name:\s*([^\r\n]+)', block)
            if not name_m:
                continue
            name = name_m.group(1).strip()
            # start state
            start_m = re.search(r'Start_State:\s*([0-9A-FXx])', block)
            start = start_m.group(1).upper() if start_m else '0'

            # edges
            edges = re.findall(r'Edge:\s*([0-9.\-E]+)\s+([01])', block)
            edges = [(float(t), int(v)) for t, v in edges]  # times are in time_scale units
            digital_signals[name] = {
                'start': start,
                'edges': edges
            }

        elif block.startswith("Digital_Bus"):
            name_m = re.search(r'Name:\s*([^\r\n]+)', block)
            if not name_m:
                continue
            name = name_m.group(1).strip()
            start_m = re.search(r'Start_State:\s*([0-9A-Fa-f]+)', block)
            start = start_m.group(1).upper() if start_m else '0'
            # bus edges with hex values (eg "Edge: 140000.0 0F")
            edges = re.findall(r'Edge:\s*([0-9.\-E]+)\s+([0-9A-Fa-f]+)', block)
            edges = [(float(t), v.upper()) for t, v in edges]
            digital_buses[name] = {
                'start': start,
                'edges': edges
            }

    return time_scale, digital_signals, digital_buses

# ---------- CONSTRUCCIÓN DE TRANSICIONES POR BIT ----------
def build_bit_traces_from_bus(bus_name, bus_info, time_scale, msb, lsb, base_index):
    """
    Convierte un Digital_Bus (con edges con valores hex) a trazas por bit.
    Devuelve dict: bit_index -> list of (time_seconds, voltage)
    """
    width = msb - lsb + 1

    # estado inicial
    start_hex = bus_info['start']
    try:
        start_bits = hex_to_bits(start_hex, width) if len(start_hex) > 0 else [0]*width
    except:
        start_bits = [0]*width

    # reverse SOLO para A y B
    reverse = (bus_name == "A[3:0]" or bus_name == "B[3:0]")

    # Inicialización de trazas
    bit_traces = {
        (base_index + (width - 1 - i if reverse else i)):
            [(0.0, VDD if start_bits[i] == 1 else 0.0)]
        for i in range(width)
    }

    # Procesar edges
    last_bits = start_bits[:]

    for t_units, hexval in sorted(bus_info['edges'], key=lambda x: x[0]):
        t_s = t_units * time_scale
        bits = hex_to_bits(hexval, width)

        for i in range(width):
            bit_idx = base_index + (width - 1 - i if reverse else i)

            new_v = VDD if bits[i] == 1 else 0.0
            last_v = VDD if last_bits[i] == 1 else 0.0

            if new_v != last_v:
                bit_traces[bit_idx].append((t_s, new_v))

        last_bits = bits

    return bit_traces


# ---------- GENERAR PWL SQUARE (con epsilon en pre-edge) ----------
def build_pwl_points(points, time_eps):
    """
    points: lista de (t_sec, v) ordenadas por t
    Construye lista de puntos PWL con epsilon para transiciones netas.
    """
    if not points:
        return [(0.0, 0.0)]
    # Normalizar: asegurarnos que exista punto en t=0
    if points[0][0] > 0:
        points = [(0.0, points[0][1])] + points

    pwl = []
    current_v = points[0][1]
    pwl.append((0.0, current_v))

    for i in range(1, len(points)):
        t, v = points[i]
        if v == current_v:
            # nothing changed (possible duplicate) -> skip
            continue
        t_pre = max(0.0, t - time_eps)
        # pre-transition hold
        if pwl and (abs(pwl[-1][0] - t_pre) < 1e-18) and pwl[-1][1] == current_v:
            # already have same point - skip
            pass
        else:
            pwl.append((t_pre, current_v))
        # transition
        pwl.append((t, v))
        current_v = v

    return pwl

# ---------- MAIN ----------
def convert_tim_to_cir(tim_file, out_file=None):
    if out_file is None:
        out_file = tim_file.replace('.tim', DEFAULT_OUT_SUFFIX)

    time_scale, dig_sigs, dig_buses = parse_tim(tim_file)
    epsilon = max(time_scale * EPSILON_FACTOR, MIN_EPS)

    # prepare container para trazas finales: mapping node -> list of (t,v)
    node_traces = defaultdict(list)

    # 1) Señales digitales simples (clk, init, rst, done, pp... but nosotros guardamos las de entrada)
    for name, info in dig_sigs.items():
        # solo nos interesan clk, init, rst... pero parseamos todo por si hace falta
        start = info['start']
        edges = sorted(info['edges'], key=lambda x: x[0])
        # convertir tiempos a segundos
        pts = []
        # start state: puede ser '0','1' o 'X'
        start_v = VDD if start == '1' else 0.0
        pts.append((0.0, start_v))
        for t_units, val in edges:
            t_s = t_units * time_scale
            v = VDD if int(val) == 1 else 0.0
            pts.append((t_s, v))
        # mapear nombre si está en SIGNAL_MAP
        if name in SIGNAL_MAP:
            vname, node = SIGNAL_MAP[name]
            node_traces[(vname, node)] = build_pwl_points(pts, epsilon)
        else:
            # other signals: keep if user wanted, but we ignore for now
            # store under safe name (in case you want to inspect)
            safe = safe_name(name)
            node_traces[(f"V_{safe}", name)] = build_pwl_points(pts, epsilon)

    # 2) Buses (A[3:0], B[3:0]) -> extraer bits
    for bus_name, (bus_node_base, msb, lsb, base_index) in BUS_MAP.items():
        if bus_name not in dig_buses:
            # no está presente en el .tim -> igual generamos a partir del Start_State si existe
            if bus_name in dig_buses:
                bus_info = dig_buses[bus_name]
            else:
                continue
        else:
            bus_info = dig_buses[bus_name]

        bit_traces = build_bit_traces_from_bus(bus_name, bus_info, time_scale, msb, lsb, base_index)
        # cada bit_traces key es el índice absoluto (p.e. 0..3 para A, 4..7 para B)
        for bit_idx, pts in bit_traces.items():
            # ordenar y construir PWL
            pts_sorted = sorted(pts, key=lambda x: x[0])
            node_name = f"ui_in[{bit_idx}]"
            vname = f"V_ui_in[{bit_idx}]"
            node_traces[(vname, node_name)] = build_pwl_points(pts_sorted, epsilon)

    # 3) Si se tiene 'rst' como Digital_Signal en el TIM con nombre 'rst' -> lo mapeará a V_rst_n por SIGNAL_MAP
    # (ya hecho en paso 1)

    # Calcular tiempo maximo de simulación
    max_t = 0.0
    for pts in node_traces.values():
        for t, _ in pts:
            if t > max_t:
                max_t = t
    sim_time = max(1e-9, max_t * 1.1)  # un poco más que el máximo

    # Escribir archivo .cir
    with open(out_file, 'w') as f:
        f.write(f"* Generated from {tim_file}\n")
        f.write(f"* VDD Level: {VDD} V\n\n")
        f.write(".lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt\n\n")
        # Ajusta el .tran según necesites; aquí usamos timestep = time_scale*10 para buena resolución
        timestep = max(time_scale * 10.0, 1e-12)
        f.write(f".tran {format(timestep, '.12g')} {format(sim_time, '.12g')}\n")
        f.write(f".print tran format=raw file={out_file.replace('.cir','')}.raw v(*)\n\n")
        f.write("* Power rails\n")
        f.write(f"Vvdd VPWR 0 DC {VDD}\n")
        f.write("Vgnd VGND 0 DC 0\n\n")

        # Escribimos cada fuente PWL
        for (vname, node), pts in sorted(node_traces.items(), key=lambda x: x[0][0]):
            # formatear la lista de puntos
            if not pts:
                pwl_str = f"PWL(0 0 {sim_time} 0)"
            else:
                parts = []
                for t, v in pts:
                    parts.append(f"{format(t, '.12g')} {format(v, '.6g')}")
                pwl_str = "PWL(" + " ".join(parts) + ")"
            f.write(f"* {node}\n")
            f.write(f"{vname} {node} 0 {pwl_str}\n\n")

        f.write(f".include \"./{tim_file.replace('.tim','.spice')}\"\n")
        f.write(".end\n")

    # Report
    print(f"Salida escrita: {out_file}")
    print(f"Time scale: {time_scale} s (epsilon={epsilon} s)")
    print(f"Sim time sugerido: {sim_time} s")
    print(f"Señales procesadas: {len(node_traces)}")
    for (vname, node), pts in node_traces.items():
        print(f" - {vname} -> {node} : {len(pts)} puntos, ultimo tiempo {pts[-1][0] if pts else 0.0}")

    return out_file

# ---------- EXEC ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tim_to_cir_asic.py <archivo.tim> [<salida.cir>]")
        sys.exit(1)
    tim_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) >= 3 else None
    convert_tim_to_cir(tim_file, out_file)
