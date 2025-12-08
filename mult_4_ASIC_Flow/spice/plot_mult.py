import ltspice
import matplotlib.pyplot as plt
import numpy as np

# Ruta al archivo .raw
filepath = 'tt_um_mult_4.raw'

# Leer el archivo .raw
l = ltspice.Ltspice(filepath)
l.parse()

# Obtener el tiempo
time = l.get_time()

# ===== Función auxiliar =====
def read_signal(ltspice_obj, signal_name):
    try:
        sig = ltspice_obj.get_data(signal_name)
        if sig is not None:
            print(f"✓ {signal_name}")
            return sig
        else:
            print(f"✗ {signal_name} (None)")
            return None
    except:
        print(f"✗ {signal_name} (Error)")
        return None

print("Leyendo señales de control...")
CLK   = read_signal(l, 'v(clk)')
RST_N = read_signal(l, 'v(rst_n)')

print("\nLeyendo UI_IN...")
UI_IN = []
for i in range(8):
    s = read_signal(l, f'v(ui_in[{i}])')
    if s is not None:
        UI_IN.append(s)

print("\nLeyendo UO_OUT...")
UO_OUT = []
for i in range(8):
    s = read_signal(l, f'v(uo_out[{i}])')
    if s is not None:
        UO_OUT.append(s)

print("\nLeyendo UIO_OUT...")
UIO_OUT = []
for i in range(8):
    s = read_signal(l, f'v(uio_out[{i}])')
    if s is not None:
        UIO_OUT.append(s)

print("\nLeyendo UIO_IN...")
UIO_IN = []
for i in range(8):
    s = read_signal(l, f'v(uio_in[{i}])')
    if s is not None:
        UIO_IN.append(s)

# Validación
if len(UI_IN) == 0 and len(UO_OUT) == 0 and len(UIO_OUT) == 0:
    print("\n⚠ No se encontraron señales. Señales disponibles:")
    for name in l.get_data_names():
        print(f" - {name}")
    exit()

# ===== Listas de señales =====
signals = []
sig_names = []

signals_in = []
sig_names_in = []

# CLK
if CLK is not None:
    signals.append(CLK)
    sig_names.append('CLK')
    signals_in.append(CLK)
    sig_names_in.append('CLK')

# rst
if RST_N is not None:
    signals.append(RST_N)
    sig_names.append('RST')


# Señales de estado
if len(UIO_IN) > 0:
    signals.append(UIO_IN[0])
    sig_names.append('INIT')

if len(UIO_OUT) > 0:
    signals.append(UIO_OUT[0])
    sig_names.append('DONE')

# UO_OUT bits
for i, sig in enumerate(UO_OUT):
    signals.append(sig)
    sig_names.append(f'UO_OUT[{i}]')

# Operandos
for i, sig in enumerate(UI_IN):
    signals_in.append(sig)
    if i < 4:
        sig_names_in.append(f'A[{i}]')
    else:
        sig_names_in.append(f'B[{i-4}]')

print(f"\n✓ Total señales válidas: {len(signals)}")

# =============================
# GRAFICA 1 - OPERANDS
# =============================
num_signals_in = len(signals_in)
fig, axes = plt.subplots(num_signals_in, 1, figsize=(14, num_signals_in*0.7), sharex=True)

for i, (ax, sig) in enumerate(zip(axes, signals_in)):
    color = plt.cm.viridis(i / num_signals_in)
    ax.plot(time, sig, linewidth=2.2, color=color)
    ax.set_ylabel(sig_names_in[i], rotation=0, ha='right', va='center', fontsize=9)

    ax.grid(True, which='both', linestyle='--', linewidth=0.4, alpha=0.5)
    ax.minorticks_on()
    ax.set_ylim(-0.5, 3.5)

    estado_final = sig[-1] if len(sig) > 0 else 0
    ax.text(time[-1], estado_final, f'  {int(estado_final)}V',
            va='center', ha='left',
            fontsize=9, fontweight='bold', color=color)

axes[-1].set_xlabel('Time (s)', fontsize=11)
plt.suptitle('Operands A=5 and B=13 of the Multiplier', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()

# =============================
# GRAFICA 2 - ALL SIGNALS
# =============================
num_signals = len(signals)
fig, axes = plt.subplots(num_signals, 1, figsize=(14, num_signals*0.7), sharex=True)

for i, (ax, sig) in enumerate(zip(axes, signals)):
    ax.plot(time, sig, linewidth=2.0, color=plt.cm.viridis(i/num_signals))
    ax.set_ylabel(sig_names[i], rotation=0, ha='right', va='center', fontsize=9)
    ax.grid(True, which='both', linestyle='--', linewidth=0.4, alpha=0.5)
    ax.minorticks_on()
    ax.set_ylim(-0.5, 3.5)

# ----- Línea vertical en la mitad del tiempo -----
mid_idx = len(time) // 2
mid_time = time[mid_idx]

for ax in axes:
    ax.axvline(mid_time, linestyle='--', linewidth=1.6, alpha=0.9)

axes[-1].set_xlabel('Time (s)', fontsize=11)
plt.suptitle('Signals of Post-layout verified', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()


# =============================
# GRAFICA 3 - OFFSET VIEW
# =============================
plt.figure(figsize=(16, 10))
offset = 4
for i, sig in enumerate(signals):
    plt.plot(time, sig + i*offset, label=sig_names[i], linewidth=2.0)

plt.xlabel('Time (s)', fontsize=12, fontweight='bold')
plt.ylabel('Voltage (V) with offset', fontsize=12, fontweight='bold')
plt.title('All Signals (Offset View)', fontsize=14, fontweight='bold')
plt.grid(True, which='both', linestyle='--', linewidth=0.4, alpha=0.5)
plt.minorticks_on()
plt.legend(loc='upper right', fontsize=8, ncol=3)
plt.tight_layout()
plt.show()

# =============================
# GRAFICA 4 - DECIMAL BUS
# =============================
fig, ax2 = plt.subplots(1, 1, figsize=(14, 10), sharex=True)

threshold = 1.5

# UI_IN decimal
ui_in_decimal = np.zeros_like(time)
for i, sig in enumerate(UI_IN):
    digital_bit = (sig > threshold).astype(int)
    ui_in_decimal += digital_bit * (2 ** i)

# UO_OUT decimal
uo_out_decimal = np.zeros_like(time)
for i, sig in enumerate(UO_OUT):
    digital_bit = (sig > threshold).astype(int)
    uo_out_decimal += digital_bit * (2 ** i)

ax2.plot(time, uo_out_decimal, linewidth=2.5)

ax2.set_ylabel('UO_OUT:PP Decimal', fontsize=11, fontweight='bold')
ax2.set_title('UO_OUT:PP (8-bit to Decimal)', fontsize=12, fontweight='bold')
ax2.grid(True, which='both', linestyle='--', linewidth=0.4, alpha=0.5)
ax2.minorticks_on()
ax2.set_ylim([-5, 260])

# Punto medio
mid_idx = len(time)//2
x_mid = time[mid_idx]
y_mid = uo_out_decimal[mid_idx]

ax2.scatter(x_mid, y_mid, color='red', zorder=5)
ax2.text(x_mid, y_mid, f'  {int(y_mid)}',
         color='red', fontsize=10, fontweight='bold',
         va='bottom', ha='left')

plt.tight_layout()
plt.show()

print(f"Valor entero final: {int(uo_out_decimal[-1])}")
print("✓ Graficación completada")
print(f"Puntos de datos: {len(time)}")
print(f"Rango de tiempo: {time[0]:.2e} s a {time[-1]:.2e} s")
