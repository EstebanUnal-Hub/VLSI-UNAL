#!/usr/bin/env python3
"""
plot_filtered_signals_limited.py (modificado)

Versión modificada para:
 - Mostrar solo las "importantes" + el bus PC completo.
 - Omitir variables "por bit" (ej: PC_0, signal_3) de la lista principal.
 - Respetar un límite máximo de señales (por defecto 10).
 - Si PC[msb:lsb] está presente, dibuja todos sus bits en una figura separada (overlay).
 - AÑADIDO: gráfica adicional que reconstruye el entero del bus (p.ej. PC[23:0])
   y lo dibuja vs tiempo.
"""
import argparse
import os
import re
import numpy as np
import matplotlib.pyplot as plt

try:
    import ltspice
except Exception as e:
    raise SystemExit("Falta el paquete 'ltspice'. Instálalo: pip install ltspice") from e

# ---------------- utilidades ----------------

def is_time_var(name):
    return name.strip().lower() in ('time', 't', 'vt', 'time(s)')

def compile_patterns(patterns_list):
    compiled = []
    for p in patterns_list:
        if not p:
            continue
        try:
            compiled.append(re.compile(p, re.IGNORECASE))
        except re.error:
            compiled.append(re.compile(re.escape(p), re.IGNORECASE))
    return compiled

def matches_any(name, compiled_patterns):
    for pat in compiled_patterns:
        if pat.search(name):
            return True
    return False

def parse_bus_spec(s):
    m = re.match(r'^\s*([A-Za-z_0-9\.-]+)\s*\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*$', s)
    if not m:
        return None
    return m.group(1), int(m.group(2)), int(m.group(3))

def expand_bus_name(base, msb, lsb, all_vars):
    """Devuelve lista de nombres (según lo encontrado) para cada bit.
       Si no existe el bit en all_vars añade el nombre probable base_#."""
    bits = []
    if msb >= lsb:
        rng = range(msb, lsb-1, -1)
    else:
        rng = range(msb, lsb+1)
    for i in rng:
        found = None
        # buscar coincidencias en all_vars con varios formatos
        for cand in all_vars:
            cn = str(cand)
            # formas: base[i], base_i, V(base_i), V(base[i]) etc
            if re.search(r'\b' + re.escape(base) + r'\[' + str(i) + r'\]\b', cn, re.IGNORECASE):
                found = cand; break
            if re.search(r'\b' + re.escape(base) + r'_' + str(i) + r'\b', cn, re.IGNORECASE):
                found = cand; break
            if re.search(re.escape(base) + r'[^0-9A-Za-z]+' + str(i), cn, re.IGNORECASE):
                found = cand; break
        bits.append(found if found is not None else f"{base}_{i}")
    return bits

# ---------------- funciones de reconstrucción entera ----------------

def read_bit_array(L, varname, npts):
    """
    Intenta leer varname desde L.get_data.
    Devuelve un array numpy de longitud npts (recortado o rellenado con ceros).
    Si falla, devuelve ceros.
    """
    try:
        raw = L.get_data(varname)
    except Exception:
        raw = None
    if raw is None:
        return np.zeros(npts, dtype=np.float64)
    arr = np.array(raw, dtype=np.float64)
    if len(arr) >= npts:
        return arr[:npts]
    else:
        # pad con ceros al final
        pad = np.zeros(npts - len(arr), dtype=np.float64)
        return np.concatenate([arr, pad])

def binarize_signal(arr):
    """
    Convierte señal analógica a 0/1 por umbral.
    Umbral definido como (min+max)/2, si min==max devuelve ceros.
    """
    if arr.size == 0:
        return np.zeros_like(arr, dtype=np.uint8)
    mn = np.min(arr)
    mx = np.max(arr)
    if np.isclose(mn, mx):
        return (arr > (mn + 1e-12)).astype(np.uint8)  # todos 0 salvo si >mn
    thresh = (mn + mx) / 2.0
    return (arr > thresh).astype(np.uint8)

def reconstruct_bus_integer_from_bits(L, t, bits_list, lsb, msb):
    """
    bits_list: lista ordenada de nombres de bits desde MSB->LSB (misma orden que expand_bus_name)
    lsb, msb: indices numéricos (por ejemplo 0..22)
    Devuelve entero_array (uint64) y dict encontrado_bits {idx: varname o None}
    """
    npts = len(t)
    # construir mapa de índice -> varname (si el nombre real tiene índice)
    # bits_list is ordered from msb down to lsb based on expand_bus_name
    # we need to know actual index for each entry
    # attempt to parse index from string if the entry is like 'PC_5' or 'PC[5]' or 'V(PC[5])'
    found_map = {}
    # create mapping of index -> varname_or_none
    expected = list(range(msb, lsb-1, -1)) if msb >= lsb else list(range(msb, lsb+1))
    for idx, expected_idx in enumerate(expected):
        item = bits_list[idx] if idx < len(bits_list) else None
        if item is None:
            found_map[expected_idx] = None
            continue
        # if item appears exactly in netlist variables, use it; otherwise it's a guessed name
        found_map[expected_idx] = item

    # Now for each expected_idx read and binarize
    ints = np.zeros(npts, dtype=np.uint64)
    valid_bits = 0
    for bit_idx in expected:
        var = found_map.get(bit_idx)
        if var is None:
            bit_arr = np.zeros(npts, dtype=np.uint8)
        else:
            arr = read_bit_array(L, var, npts)
            if arr is None:
                bit_arr = np.zeros(npts, dtype=np.uint8)
            else:
                bit_arr = binarize_signal(arr)
                # count as valid if not all zeros and not all the same?
                if np.any(bit_arr != 0):
                    valid_bits += 1
        # shift into integer (bit_idx is the actual bit position)
        # note: ints += (bit_arr.astype(uint64) << bit_idx) but bit_idx may be large; safe with uint64
        ints |= (bit_arr.astype(np.uint64) << np.uint64(bit_idx))
    return ints, found_map, valid_bits

# ---------------- script principal ----------------

def main():
    p = argparse.ArgumentParser(description="Graficador limitado: importantes + PC bus completo (max señales configurable) y entero del bus.")
    p.add_argument('rawfile', help='Archivo .raw de LTSpice/Xyce')
    p.add_argument('--signals', help='Lista csv de señales importantes (ej: CLK,RESETN,SPI_MISO)', default=None)
    p.add_argument('--buses', help='Lista csv de buses a incluir (ej: PC[23:0])', default='PC[23:0]')
    p.add_argument('--max-signals', type=int, default=10, help='Máximo total de señales (incluye PC como grupo aparte)')
    p.add_argument('--cmap', default='tab20')
    p.add_argument('--save', default=None, help='Directorio donde guardar png (si no, muestra en pantalla)')
    args = p.parse_args()

    raw = args.rawfile
    if not os.path.exists(raw):
        raise SystemExit(f"No existe el archivo RAW: {raw}")

    L = ltspice.Ltspice(raw)
    print("Parseando RAW...")
    L.parse()

    # variables disponibles
    try:
        cand = L.get_variables()
    except Exception:
        cand = getattr(L, 'variables', None) or list(getattr(L, 'dict_data', {}).keys())
    all_vars = [str(v) for v in cand if not is_time_var(str(v))]

    # señales "importantes" por defecto (buscamos por contains; puedes personalizar)
    default_important = [
        r'\bCLK\b', r'CLK', r'V\(CLK\)',
        r'\bRESET\b', r'RESETN', r'RESET',
        r'\bSI\b', r'\bSO\b',
        r'\bBUSY\b', r'WBUSY', r'RBUSY',
        r'V\(SO\)', r'V\(SI\)', r'V\(S\\?I\)',
        r'\bSTATE\b', r'\bCP\b', r'CP'
    ]

    compiled = []
    if args.signals:
        user = [s.strip() for s in args.signals.split(',') if s.strip()]
        compiled += compile_patterns([re.escape(s) for s in user])
    # si no se especifican señales, usamos la lista por defecto
    if not compiled:
        compiled += compile_patterns(default_important)

    # Filtrar variables que coincidan con patrones importantes
    matched = [v for v in all_vars if matches_any(v, compiled)]

    # Excluir variables "por bit" de la selección principal (ej: nombres que terminan en _\d+ o contienen [\d+])
    def is_bit_name(v):
        # V(PC_0) o PC_0 o PC[0] o V(PC[0])
        if re.search(r'[_\[]\d+\]', v) or re.search(r'[_\[]\d+$', v):
            return True
        # tambien si termina en _<num> (sin paréntesis)
        if re.search(r'_[0-9]+$', v):
            return True
        return False

    matched_nobits = [v for v in matched if not is_bit_name(v)]

    # Resolver buses solicitados (ej: PC[23:0]) y obtener la lista completa de bits
    bus_list = []
    if args.buses:
        for b in args.buses.split(','):
            b = b.strip()
            if not b: continue
            bs = parse_bus_spec(b)
            if bs:
                base, msb, lsb = bs
                bits = expand_bus_name(base, msb, lsb, all_vars)
                bus_list.append((base, msb, lsb, bits))
            else:
                # no es 'BASE[MSB:LSB]', intentar buscar literal
                bus_list.append((b, None, None, [x for x in all_vars if b.lower() in x.lower()]))

    # Construir lista final de señales a mostrar (limitada por --max-signals)
    maxsig = max(1, int(args.max_signals))

    # Reservamos 1 "slot" para el grupo bus (aunque sus bits se dibujen por separado).
    reserved_for_bus = 1 if bus_list else 0
    slots_for_individuals = maxsig - reserved_for_bus
    if slots_for_individuals < 1 and reserved_for_bus == 1:
        slots_for_individuals = 1

    # Tomar las primeras N señales no-bit encontradas
    selected_individuals = []
    for v in matched_nobits:
        if v not in selected_individuals:
            selected_individuals.append(v)
        if len(selected_individuals) >= slots_for_individuals:
            break

    # Si no encontramos suficientes por "default_important", intentar incluir otras que no sean bits
    if len(selected_individuals) < slots_for_individuals:
        for v in all_vars:
            if v in selected_individuals: continue
            if is_bit_name(v): continue
            selected_individuals.append(v)
            if len(selected_individuals) >= slots_for_individuals:
                break

    print(f"Señales individuales a graficar (max {slots_for_individuals}): {len(selected_individuals)}")
    for s in selected_individuals:
        print("  -", s)
    if bus_list:
        print("Buses detectados:")
        for base,msb,lsb,bits in bus_list:
            print(f"  - {base}[{msb}:{lsb}] -> {len(bits)} bits (primeros 8 mostrados): {bits[:8]}")

    # Leer datos
    t = np.array(L.get_time())

    signals = []
    for name in selected_individuals:
        try:
            data = np.array(L.get_data(name))
        except Exception:
            print("⚠️  No se pudo extraer datos para:", name)
            continue
        mn = min(len(t), len(data))
        signals.append((name, t[:mn], data[:mn]))

    # graficar individuales
    def get_colormap(n, cmap='tab20'):
        cm = plt.get_cmap(cmap)
        def color(i):
            if n<=1: return cm(0.0)
            return cm(float(i)/float(max(1,n-1)))
        return color

    cmap_fn = get_colormap(len(signals), args.cmap)

    if signals:
        fig, axes = plt.subplots(len(signals), 1, figsize=(12, 1.8*len(signals)), sharex=True)
        if len(signals) == 1:
            axes = [axes]
        for i, (name, tt, data) in enumerate(signals):
            axes[i].plot(tt, data, color=cmap_fn(i), linewidth=1)
            axes[i].set_ylabel(name, rotation=0, ha='right', va='center')
            axes[i].grid(alpha=0.2)
            mn, mx = np.min(data), np.max(data)
            if np.isfinite(mn) and np.isfinite(mx):
                if np.allclose(mn,mx):
                    axes[i].set_ylim(mn-0.5, mx+0.5)
                else:
                    pad = 0.05*(mx-mn)
                    axes[i].set_ylim(mn-pad, mx+pad)
        axes[-1].set_xlabel('Time (s)')
        fig.suptitle('Señales importantes (filtradas)')
        fig.tight_layout(rect=[0,0,1,0.96])
        if args.save:
            os.makedirs(args.save, exist_ok=True)
            out = os.path.join(args.save, os.path.basename(raw) + '.selected.png')
            fig.savefig(out, dpi=180)
            print('Guardado:', out)
            plt.close(fig)
        else:
            plt.show()

    # graficar cada bus (overlay con offsets) en figuras separadas
    for base, msb, lsb, bits in bus_list:
        bit_signals = []
        for bit in bits:
            if bit in all_vars:
                try:
                    d = np.array(L.get_data(bit))
                except Exception:
                    continue
                mn = min(len(t), len(d))
                bit_signals.append((bit, t[:mn], d[:mn]))
        if not bit_signals:
            print(f"⚠️  No se encontraron bits válidos para el bus {base}")
            continue
        plt.figure(figsize=(12, max(4, 0.25*len(bit_signals))))
        ranges = [np.ptp(s) if np.ptp(s) > 0 else 1.0 for (_,_,s) in bit_signals]
        step = max(ranges) + 1.0
        offset = 0.0
        cmap_bus = get_colormap(len(bit_signals), args.cmap)
        for i, (name, tt, data) in enumerate(bit_signals):
            plt.plot(tt, data + offset, color=cmap_bus(i), linewidth=0.9, label=name)
            offset += step
        plt.xlabel('Time (s)')
        plt.title(f'Bus {base} bits (overlay)')
        if len(bit_signals) <= 32:
            plt.legend(loc='upper right', ncol=2, fontsize='small')
        plt.grid(alpha=0.2)
        plt.tight_layout()
        if args.save:
            out = os.path.join(args.save, os.path.basename(raw) + f'.bus_{base}.png')
            plt.savefig(out, dpi=180)
            print('Guardado:', out)
            plt.close()
        else:
            plt.show()

        # ----------------- Plot entero reconstruido del bus -----------------
        # Intentar reconstruir entero solo si msb/lsb están definidos (formato BASE[MSB:LSB])
        if msb is not None and lsb is not None:
            ints, found_map, valid_bits = reconstruct_bus_integer_from_bits(L, t, bits, lsb, msb)
            if valid_bits == 0:
                print(f"⚠️  No se detectaron bits activos para {base}[{msb}:{lsb}] — se omite el plot entero.")
                continue
            plt.figure(figsize=(12,4))
            plt.plot(t, ints, linewidth=1.0)
            plt.xlabel('Time (s)')
            plt.ylabel(f'{base}[{msb}:{lsb}] as integer')
            plt.title(f'Reconstrucción entera del bus {base}[{msb}:{lsb}] (bits válidos: {valid_bits})')
            plt.grid(alpha=0.25)
            plt.tight_layout()
            if args.save:
                outint = os.path.join(args.save, os.path.basename(raw) + f'.{base}_int.png')
                plt.savefig(outint, dpi=180)
                print('Guardado entero:', outint)
                plt.close()
            else:
                plt.show()
        else:
            # si no hay rango definido, intentamos inferir algo pero lo omitimos para evitar resultados incorrectos
            print(f"Nota: el bus {base} no está en formato BASE[MSB:LSB]; no se generó el entero automáticamente.")

if __name__ == '__main__':
    main()
