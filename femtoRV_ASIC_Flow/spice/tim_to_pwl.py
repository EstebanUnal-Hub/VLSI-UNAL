#!/usr/bin/env python3
"""
tim_to_cir_femto.py
Convierte un .tim (GTKWave) a .cir (ngspice). Maneja Digital_Signal y Digital_Bus,
descompone buses en bits y genera fuentes PWL. Diseñado para .tim grandes (femto).
Uso:
  python3 tim_to_cir_femto.py tt_um_femto.tim [tt_um_femto.cir]
"""
import re, sys, math
from pathlib import Path
from collections import OrderedDict

# ---------- CONFIG ----------
VDD = 3.3
EPSILON_FACTOR = 1e-3   # epsilon ~ EPSILON_FACTOR * time_scale
MIN_EPS = 1e-12
DEFAULT_OUT_SUFFIX = ".cir"

# ---------- UTIL ----------
def safe_name(s):
    return re.sub(r'[^\w]', '_', s)

def hex_to_bits(hexstr, width):
    try:
        val = int(hexstr, 16)
    except Exception:
        return [0]*width
    bits = [(val >> i) & 1 for i in range(width)]
    bits = list(reversed(bits))
    if len(bits) < width:
        bits = [0]*(width - len(bits)) + bits
    return bits[-width:]

# ---------- PARSER TIM ----------
def parse_tim(path):
    txt = Path(path).read_text()
    m = re.search(r'Time_Scale:\s*([0-9.Ee+\-]+)', txt)
    time_scale = float(m.group(1)) if m else 1e-12

    blocks = re.split(r'(?=Digital_Signal|Digital_Bus)', txt)
    digital_signals = OrderedDict()
    digital_buses = OrderedDict()

    for block in blocks:
        block = block.strip()
        if not block: continue
        if block.startswith("Digital_Signal"):
            nm = re.search(r'Name:\s*([^\r\n]+)', block)
            if not nm: continue
            name = nm.group(1).strip()
            sm = re.search(r'Start_State:\s*([0-9A-FXx])', block)
            start = sm.group(1).upper() if sm else '0'
            edges = re.findall(r'Edge:\s*([0-9.\-E]+)\s+([01])', block)
            edges = [(float(t), int(v)) for t, v in edges]
            digital_signals[name] = {'start': start, 'edges': edges}
        elif block.startswith("Digital_Bus"):
            nm = re.search(r'Name:\s*([^\r\n]+)', block)
            if not nm: continue
            name = nm.group(1).strip()
            sm = re.search(r'Start_State:\s*([0-9A-Fa-f]+)', block)
            start = sm.group(1).upper() if sm else '0'
            edges = re.findall(r'Edge:\s*([0-9.\-E]+)\s+([0-9A-Fa-f]+)', block)
            edges = [(float(t), v.upper()) for t, v in edges]
            digital_buses[name] = {'start': start, 'edges': edges}
    return time_scale, digital_signals, digital_buses

# ---------- PWL helper ----------
def build_pwl_from_points(points, eps):
    if not points:
        return [(0.0, 0.0)]
    if points[0][0] > 0:
        points = [(0.0, points[0][1])] + points
    pwl = [(0.0, points[0][1])]
    cur = points[0][1]
    for i in range(1, len(points)):
        t, v = points[i]
        if v == cur:
            continue
        tpre = max(0.0, t - eps)
        if not (abs(pwl[-1][0] - tpre) < 1e-18 and pwl[-1][1] == cur):
            pwl.append((tpre, cur))
        pwl.append((t, v))
        cur = v
    return pwl

# ---------- MAIN ----------
def convert_tim_to_cir(tim_path, out_path=None):
    tim_path = Path(tim_path)
    if out_path is None:
        out_path = tim_path.with_suffix(DEFAULT_OUT_SUFFIX)
    else:
        out_path = Path(out_path)

    time_scale, dig_sigs, dig_buses = parse_tim(tim_path)
    epsilon = max(time_scale * EPSILON_FACTOR, MIN_EPS)

    node_traces = OrderedDict()

    # 1) Signals
    for name, info in dig_sigs.items():
        start = info['start']
        edges = sorted(info['edges'], key=lambda x: x[0])
        pts = [(0.0, VDD if start == '1' else 0.0)]
        for t_units, val in edges:
            pts.append((t_units * time_scale, VDD if int(val) == 1 else 0.0))
        vname = f"V_{safe_name(name)}"
        node_traces[(vname, name)] = build_pwl_from_points(pts, epsilon)

    # 2) Buses -> bits (solo añade bits si no existen ya como Digital_Signal)
    for bus_name, info in dig_buses.items():
        start_hex = info['start'] if info['start'] else "0"
        width = max(1, len(start_hex) * 4)
        # adjust width if edges contain longer hex
        for _, val in info['edges']:
            if len(val) > 1:
                width = max(width, len(val) * 4)
        # if bus name contains [hi:lo], use exactly that range
        rng = re.search(r'\[(\d+):(\d+)\]', bus_name)
        if rng:
            hi = int(rng.group(1)); lo = int(rng.group(2))
            width = hi - lo + 1
            indices = list(range(lo, hi+1))
        else:
            indices = list(range(width))
        start_bits = hex_to_bits(start_hex, width)
        # create per-bit traces (index 0..width-1 maps to indices[0..])
        bit_traces = {i: [(0.0, VDD if start_bits[i] == 1 else 0.0)] for i in range(width)}
        last_bits = start_bits[:]
        for t_units, hexval in sorted(info['edges'], key=lambda x: x[0]):
            t = t_units * time_scale
            bits = hex_to_bits(hexval, width)
            for i in range(width):
                v_new = VDD if bits[i] == 1 else 0.0
                v_last = VDD if last_bits[i] == 1 else 0.0
                if v_new != v_last:
                    bit_traces[i].append((t, v_new))
            last_bits = bits
        # store only if not present as signal
        for i in range(width):
            idx = indices[i]
            # build node name consistent with bus (e.g., ui_in[3])
            node = re.sub(r'\[\d+:\d+\]$', f'[{idx}]', bus_name) if rng else f"{bus_name}[{idx}]"
            if node in dig_sigs:
                continue
            vname = f"V_{safe_name(bus_name)}[{idx}]"
            node_traces[(vname, node)] = build_pwl_from_points(bit_traces[i], epsilon)

    # compute sim time and timestep
    max_t = 0.0
    for pts in node_traces.values():
        for t, _ in pts:
            if t > max_t: max_t = t
    sim_time = max(1e-9, max_t * 1.1)
    timestep = max(time_scale * 10.0, 1e-12)

    # write .cir
    with out_path.open("w") as f:
        f.write(f"* Generated from {tim_path.name}\n")
        f.write(f"* VDD Level: {VDD} V\n\n")
        f.write(".lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt\n\n")
        f.write(f".tran {format(timestep, '.12g')} {format(sim_time, '.12g')}\n")
        f.write(f".print tran format=raw file={out_path.with_suffix('').name}.raw v(*)\n\n")
        f.write("* Power rails\n")
        f.write(f"Vvdd VPWR 0 DC {VDD}\n")
        f.write("Vgnd VGND 0 DC 0\n\n")
        for (vname, node), pts in node_traces.items():
            parts = []
            for t, v in pts:
                parts.append(f"{format(t, '.12g')} {format(v, '.6g')}")
            pwl = "PWL(" + " ".join(parts) + ")"
            f.write(f"* {node}\n")
            f.write(f"{vname} {node} 0 {pwl}\n\n")
        f.write(f".include \"./{tim_path.with_suffix('.spice').name}\"\n")
        f.write(".end\n")

    print(f"Wrote: {out_path}")
    print(f"Time scale: {time_scale} s  (epsilon={epsilon} s)")
    print(f"Sim time: {sim_time} s  timestep: {timestep} s")
    print(f"Signals (PWL sources) written: {len(node_traces)}")
    return out_path

# ---------- CLI ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 tim_to_cir_femto.py <archivo.tim> [<salida.cir>]")
        sys.exit(1)
    tim = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert_tim_to_cir(tim, out)
