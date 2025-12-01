#!/usr/bin/env python3
"""
tim_to_pwl_filtered.py

Versión mejorada del convertidor TIM -> .cir (PWL) que:
 - Soporta Digital_Signal y Digital_Bus (p.ej. PC[23:0])
 - Convierte valores bin/hex/dec a vectores de bits
 - Genera PWL tipo "square" por cada bit (sin rampas)
 - Filtra salidas para generar SOLO las fuentes que ya existen en un .cir/.spice de referencia
 - Permite forzar inclusión de buses con --buses
"""
import re, os, sys, argparse

# ---------------- utilidades ----------------
def parse_bus_name(name):
    m = re.match(r'^(?P<base>[\w\-:.]+)\s*\[\s*(?P<msb>\d+)\s*:\s*(?P<lsb>\d+)\s*\]$', name)
    if m:
        return m.group('base'), int(m.group('msb')), int(m.group('lsb'))
    return name, None, None

def value_to_bitlist(value_str, width):
    if value_str is None:
        return [0]* (width if width is not None else 1)
    s = value_str.strip()
    def int_to_bits(i, w):
        if w is None:
            w = max(1, i.bit_length())
        bits = [(i >> b) & 1 for b in range(w)]
        return bits
    if re.fullmatch(r'[01]+', s, flags=re.IGNORECASE):
        bits = [int(ch) for ch in s[::-1]]
        if width is not None:
            if len(bits) < width: bits += [0]*(width - len(bits))
            else: bits = bits[:width]
        return bits
    if re.fullmatch(r'0[xX][0-9a-fA-F]+', s):
        val = int(s, 16)
        return int_to_bits(val, width)
    if re.fullmatch(r'\d+', s):
        val = int(s, 10)
        return int_to_bits(val, width)
    return [0]* (width if width is not None else 1)

def safe_node(base_name, bit_idx=None):
    safe = re.sub(r'[^\w]', '_', base_name)
    if bit_idx is None: return safe
    return f"{safe}_{bit_idx}"

def parse_tim_file(content):
    pattern = r'(Digital_Signal|Digital_Bus)\s*\n(.*?)(?=\nDigital_Signal|\nDigital_Bus|\Z)'
    blocks = re.findall(pattern, content, flags=re.DOTALL)
    parsed = []
    for kind, body in blocks:
        name_m = re.search(r'Name:\s*(.+)', body)
        if not name_m: continue
        name = name_m.group(1).strip()
        start_m = re.search(r'Start_State:\s*([01XxNnZz])', body)
        start_state = start_m.group(1).upper() if start_m else None
        init_val_m = re.search(r'Value:\s*=?\s*([0-9A-Fa-fxX]+)', body)
        init_val = init_val_m.group(1) if init_val_m else None
        edge_matches = re.findall(r'Edge:\s*([\d.Ee+-]+)\s+([^\s]+)', body)
        edges = [(float(t), v) for t, v in edge_matches]
        parsed.append({
            'kind': kind,
            'name': name,
            'start_state': start_state,
            'init_val': init_val,
            'edges': edges,
            'raw': body
        })
    return parsed

def generate_pwl_for_bit_series(edges, initial_bit, time_scale, vdd=3.3, eps=None):
    if eps is None:
        eps = max(1e-12, time_scale * 1e-6)
    pwl = []
    current = initial_bit
    pwl.append((0.0, vdd if current else 0.0))
    for t, bit in edges:
        newv = vdd if bit else 0.0
        if bit != current:
            t_sec = t * time_scale
            pre_t = max(0.0, t_sec - eps)
            pwl.append((pre_t, vdd if current else 0.0))
            pwl.append((t_sec, newv))
            current = bit
    return pwl

# ---------------- leer nodos/ fuentes existentes ----------------
def read_existing_voltage_sources(cir_path):
    """
    Extrae nombres de fuentes Vxxx del archivo (prefijo V nombre).
    Devuelve set de nodos seguros (sin prefijo V_). Ejemplo: si hay 'V_PC_0' -> 'PC_0'
    """
    if not cir_path or not os.path.exists(cir_path):
        return set()
    names = set()
    with open(cir_path, 'r', errors='ignore') as f:
        for line in f:
            # capturar líneas que definen fuente: comienzo de línea opcional espacio, Vname ...
            m = re.match(r'^\s*[Vv]([A-Za-z0-9_:-]+)\b', line)
            if m:
                names.add(m.group(1))  # ejemplo: 'PC_0' si la fuente fue 'VPC_0' en el archivo
            # También capturar si el netlist usa prefijo "V_" en nombre: V_PC_0
            m2 = re.match(r'^\s*[Vv]_(\w+)\b', line)
            if m2:
                names.add(m2.group(1))
    # Normalizar: algunos netlists usan V_<node>, otros Vnode; ya añadimos ambas posibilidades
    return set(names)

# ---------------- conversión principal ----------------
def convert_tim_to_square_pwl_filtered(tim_filename, output_filename=None, vdd=3.3,
                                      include_spice='./tt_um_femto.spice', filter_cir=None,
                                      buses_to_force=None):
    if output_filename is None:
        output_filename = tim_filename.replace('.tim', '.cir')
    spice_filename  = tim_filename.replace('.tim', '.spice')

    with open(tim_filename, 'r') as f:
        content = f.read()

    time_scale_match = re.search(r'Time_Scale:\s*([\d.Ee+-]+)', content)
    time_scale = float(time_scale_match.group(1)) if time_scale_match else 1e-12
    print(f"Time scale: {time_scale} s (unit from TIM)")

    parsed = parse_tim_file(content)
    existing_vs = read_existing_voltage_sources(filter_cir) if filter_cir else set()
    if filter_cir:
        print(f"Leídos {len(existing_vs)} fuentes V_ desde {filter_cir}")

    buses_force = set(buses_to_force or [])

    bit_sources = []

    for block in parsed:
        base, msb, lsb = parse_bus_name(block['name'])
        is_bus = (msb is not None)
        width = (abs(msb - lsb) + 1) if is_bus else 1
        edges = block['edges']

        # Decidir si incluimos este bloque: si hay filter_cir, sólo si:
        # - existe V_<safe_node> para algún bit del bus OR
        # - el base aparece en buses_force
        include_block = True
        if filter_cir:
            # Comprobar si cualquier bit del bus existe en existing_vs (V_<node> o <node>)
            any_present = False
            for i in range(width):
                node_name = safe_node(base, i if is_bus else None)
                # chequear también variantes (sin guion bajo prefijo)
                if node_name in existing_vs or node_name.lstrip('_') in existing_vs:
                    any_present = True
                    break
            if not any_present and base not in buses_force:
                include_block = False

        if not include_block:
            print(f"Omitido (no en filter): {block['name']}")
            continue

        # obtener init bits
        if block['init_val']:
            init_bits = value_to_bitlist(block['init_val'], width)
        else:
            if block['start_state'] and not is_bus:
                init_bits = [1] if block['start_state'] == '1' else [0]
            else:
                init_bits = [0]*width

        per_bit_edges = [ [] for _ in range(width) ]
        for t, val in edges:
            bitlist = value_to_bitlist(val, width)
            if len(bitlist) < width:
                bitlist += [0] * (width - len(bitlist))
            for i in range(width):
                per_bit_edges[i].append((t, bitlist[i]))

        for i in range(width):
            init_bit = init_bits[i] if i < len(init_bits) else 0
            bit_edge_seq = per_bit_edges[i]
            pwl_pts = generate_pwl_for_bit_series(bit_edge_seq, init_bit, time_scale, vdd=vdd)
            node = safe_node(base, i if is_bus else None)
            # filter again per-bit: si filter_cir existe y este bit no está en existing_vs
            if filter_cir:
                if not ( node in existing_vs or node.lstrip('_') in existing_vs or base in buses_force):
                    # saltar bit que no exista en el netlist de referencia
                    print(f"  Saltando bit no presente en .cir: {block['name']} bit {i} -> {node}")
                    continue
            bit_sources.append({
                'original_name': block['name'],
                'bit_index': i if is_bus else None,
                'node': node,
                'pwl': pwl_pts
            })
        print(f"Procesado: {block['name']}  tipo: {block['kind']}  ancho: {width}  edges: {len(edges)}")

    # --- escribir salida .cir ---
    with open(output_filename, 'w') as f:
        f.write(f"* Generated from {tim_filename}\n")
        f.write(f".lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt\n")
        f.write(f".tran 1000ns 600us\n")
        f.write(f".print tran format=raw file={os.path.splitext(output_filename)[0]}.raw v(*)\n\n")
        f.write("* Power rails\n")
        f.write("Vvdd VPWR 0 DC 3.3\n")
        f.write("Vgnd VGND 0 DC 0\n\n")
        for s in bit_sources:
            pairs = []
            for t, val in s['pwl']:
                pairs.append(f"{t:.12e} {val:.6f}")
            pwl_text = " ".join(pairs) if pairs else "0.0 0.0"
            f.write(f"* {s['original_name']} bit {s['bit_index']}\n")
            # nombre de la fuente: V_<node> para minimizar colisiones
            f.write(f"V_{s['node']} {s['node']} 0 PWL({pwl_text})\n\n")

        if include_spice:
            f.write(f".include \"{include_spice}\"\n")
        if os.path.exists(spice_filename):
            f.write(f".include \"./{spice_filename}\"\n")
        f.write(".end\n")

    print(f"\nOutput escrito: {output_filename}  (fuentes generadas: {len(bit_sources)})")
    return output_filename

# ---------------- CLI ----------------
def main():
    parser = argparse.ArgumentParser(description="TIM -> .cir PWL (filtrado y buses agrupados)")
    parser.add_argument("timfile", help="Archivo .tim de entrada")
    parser.add_argument("--out", "-o", help="Archivo .cir de salida")
    parser.add_argument("--vdd", type=float, default=3.3, help="Tensión VDD")
    parser.add_argument("--include", "-i", default="./tt_um_femto.spice", help="Archivo .spice a incluir")
    parser.add_argument("--filter-cir", "-f", default=None, help="Archivo .cir/.spice de referencia: sólo generar señales que aparezcan aquí")
    parser.add_argument("--buses", "-b", default=None, help="Lista de buses a forzar, separados por coma. Ej: PC,CP")
    args = parser.parse_args()

    if not os.path.exists(args.timfile):
        print("No se encontró el archivo TIM:", args.timfile)
        sys.exit(1)
    buses_list = [x.strip() for x in args.buses.split(',')] if args.buses else []

    convert_tim_to_square_pwl_filtered(args.timfile, output_filename=args.out, vdd=args.vdd,
                                      include_spice=args.include, filter_cir=args.filter_cir,
                                      buses_to_force=buses_list)

if __name__ == "__main__":
    main()
