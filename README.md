# FemtoRV Physical Implementation: ASIC Flow / Implementación Física de FemtoRV

Este repositorio documenta el proceso completo de diseño, síntesis e implementación física (RTL-to-GDSII) del núcleo **FemtoRV**, un procesador basado en la arquitectura RISC-V. El objetivo de este proyecto es llevar una descripción de hardware (HDL) hasta un layout listo para fabricación. Además, se utiliza **Tiny Tapeout** con el fin de realizar la fabricación del chip.

---

## 1. Processor Architecture / Arquitectura del Procesador (FemtoRV)

El FemtoRV es un núcleo RISC-V diseñado para ser extremadamente ligero y fácil de entender. Antes de iniciar el flujo físico, es crucial entender la microarquitectura que estamos implementando.

El siguiente diagrama de bloques ilustra la organización interna del procesador:

![FemtoRV Block Diagram](ruta/a/tu_diagrama_de_bloques_femtorv.png)
*(Reemplaza esta ruta con la imagen de tu diagrama de bloques)*

---

## 2. VLSI Design Flow / Flujo de Diseño VLSI (ASIC Flow)

Para materializar el FemtoRV en silicio, se siguió un flujo de diseño riguroso dividido en dos grandes etapas: **Frontend** (Diseño Lógico) y **Backend** (Diseño Físico).

### 2.1. Logic & Functional Design (Frontend) / Diseño Lógico y Funcional
Esta etapa se centra en la descripción del comportamiento del procesador y su traducción a compuertas lógicas digitales.

![Logical Design Flow](Documents/ASIC_Flow/VLSI_design_flow1.png)
*(Reference Diagram 1: Frontend Flow)*

Basado en el diagrama anterior, los pasos ejecutados fueron:

1.  **System Specification & Architectural Design (Especificación):** Definición de requisitos del FemtoRV, es decir, entradas y salidas hacia los periféricos y formas de comunicación con el procesador.
2.  **RTL Description / HDL (Diseño RTL):** Escritura del código en Verilog.
3.  **Functional Verification (Verificación Funcional):** Simulación del RTL para asegurar que el procesador ejecuta las instrucciones correctamente.
4.  **Logic Synthesis (Síntesis Lógica):** Transformación del código RTL a un *Gate Level Netlist*.
5.  **Logic Verification (Verificación Lógica):** Validación del Netlist.

### 2.2. Physical Design (Backend) / Diseño Físico
Una vez obtenidas las compuertas lógicas, el siguiente reto es colocarlas físicamente en el área del chip.

![Physical Design Flow](Documents/ASIC_Flow/VLSI_design_flow2.png)
*(Reference Diagram 2: Backend Flow)*

Siguiendo el flujo detallado en la imagen, el proceso consta de:

1.  **Partitioning & Chip Planning (Planificación):** Definición del Floorplan y pines.
2.  **Placement (Colocación):** Ubicación óptima de las celdas estándar.
3.  **Clock Tree Synthesis - CTS (Síntesis del Árbol de Reloj):** Distribución sincronizada del reloj.
4.  **Signal Routing (Enrutado):** Conexión física de todas las celdas.
5.  **Timing Closure (Cierre de Tiempos):** Verificación de *Setup* y *Hold*.
6.  **Physical Verification (Verificación Física):** DRC, LVS y generación de GDSII para fabricación.

---

## 3. Fabrication Platform & Template / Plataforma de Fabricación y Plantilla

Este proyecto fue diseñado específicamente para ser fabricado a través de **Tiny Tapeout**.

### Tiny Tapeout: Quicker, easier and cheaper to make your own chip!

**What is Tiny Tapeout? / ¿Qué es Tiny Tapeout?**
> Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.
>
> *Tiny Tapeout es un proyecto educativo que tiene como objetivo hacer que sea más fácil y barato que nunca fabricar tus diseños digitales y analógicos en un chip real.*

To learn more and get started, visit / Para aprender más visita: [tinytapeout.com](https://tinytapeout.com).

### Project Template Usage / Uso de la Plantilla del Proyecto

Para garantizar la integración correcta en el chip compartido, fue **necesario utilizar el template base oficial**. Esto asegura que el diseño cumpla con las restricciones de pines, área y configuración del entorno de Github Actions.

* **Base Template / Plantilla Base:** Tiny Tapeout Verilog Project Template.
* **Project Repository / Repositorio del Proyecto:** `EstebanUnal-Hub/VLSI-UNAL`
* **Significance / Importancia:** Esta plantilla preconfigura el entorno de **OpenLane** y las definiciones de pines necesarias para el shuttle de fabricación.

---

## 4. Tools & Environment / Herramientas y Entorno

Para replicar este diseño, se requiere un entorno basado en Linux (Ubuntu recomendado). A continuación, se describen las herramientas utilizadas y su función específica dentro del flujo ASIC descrito en la **Sección 2**.

### Tool Description / Descripción de las Herramientas

* **OpenLane (The Orchestrator):** Es la herramienta principal que automatiza todo el flujo **RTL-to-GDSII**. OpenLane conecta y coordina todas las demás herramientas (Yosys, OpenROAD, Magic, etc.) para pasar de la Sección 2.1 a la 2.2 de forma automatizada.
* **Icarus Verilog & GTKWave:** Pertenecen a la etapa de **Functional Verification** (Sección 2.1). Icarus compila y simula el código Verilog del FemtoRV, y GTKWave permite visualizar las ondas para depurar errores.
* **Yosys:** Ejecuta la **Logic Synthesis** (Sección 2.1). Traduce el código Verilog legible por humanos a una lista de compuertas (Netlist) optimizada.
* **OpenSTA:** Crítico para el **Timing Closure** (Sección 2.2). Realiza el análisis estático de tiempo para asegurar que el procesador cumpla con las frecuencias requeridas sin violaciones de *Setup* o *Hold*.
* **Magic VLSI:** Utilizado en la **Physical Verification** (Sección 2.2). Permite visualizar el layout final (.gds) y realizar comprobaciones de reglas de diseño (DRC).
* **Ngspice:** Simulador de circuitos a nivel transistor, útil para validaciones analógicas y caracterización.

---

### Installation Guide / Guía de Instalación

A continuación se detallan los comandos para configurar las herramientas en el entorno de Ubuntu.



#### 1. Yosys
Framework para síntesis Verilog-RTL 

```bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
sudo apt install make
sudo apt-get install build-essential clang bison flex libreadline-dev gawk tcl-dev libffi-dev git graphviz xdot pkg-config python3 libboost-system-dev libboost-python-dev libboost-filesystem-dev zlib1g-dev
make config-gcc
make
sudo make install
```

#### 2. Icarus Verilog
Compilador Verilog que genera netlists y soporta múltiples estándares.

```bash
sudo apt-get install iverilog
```

#### 3. GTKWave
Visualizador de ondas compatible con VCD.

```bash
sudo apt install gtkwave
```

#### 4. ngspice
Simulador SPICE de código abierto. Simulador para circuitos eléctricos y electrónicos, soporta JFETs, bipolar y transistores MOS, además de elementos pasivos como resistencias, inductores, condensadores, diodos, líneas de transmisión entre otros equipos. Todo se interconecta en un netlist. Los circuitos digitales son simulados desde compuertas a circuitos completos. Y la salida son una o más gráficas de corriente, voltaje, u otras señales eléctricas y pueden ser guardadas en un archivo de datos.

```bash
sudo apt-get install build-essential
sudo apt-get install libxaw7-dev

tar -zxvf ngspice-40.tar.gz
cd ngspice-40
mkdir release
cd release
../configure --with-x --with-readline=yes --disable-debug
make
sudo make install
```

#### 5. OpenSTA
Verificador de timing estático. Puede ser usado para verificar el timing de un diseño por medio de formatos de archivos estándar como verilog netlist, Liberty library, SDC timing constraints, SDF delay annotation y SPEF parasitics.

```bash
sudo apt-get install cmake clang gcc tcl swig bison flex

git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA
mkdir build
cd build
cmake ..
make
sudo make install
```

#### 6. Magic
Herramienta de layout. Magic es una herramienta de EDA para diseño físico basado en VLSI desarrollada inicialmente en UC Berkeley.

```bash
sudo apt-get install m4 tcsh csh libx11-dev tcl-dev tk-dev libcairo2-dev mesa-common-dev libglu1-mesa-dev libncurses-dev

git clone https://github.com/RTimothyEdwards/magic
cd magic
./configure
make
sudo make install
```

#### 7. OpenLane & Docker
Flujo RTL-to-GDSII.

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt install -y build-essential python3 python3-venv python3-pip make git

sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

sudo groupadd docker
sudo usermod -aG docker $USER
```

Instalación de OpenLane:

```bash
cd $HOME
git clone https://github.com/The-OpenROAD-Project/OpenLane
cd OpenLane
make
make test
```

#### 8. PDKs & Xyce

**8.1. Instalación de Open PDK (SKY130)**

El PDK (Process Design Kit) de SkyWater 130nm es necesario para la implementación física del diseño.

```bash
git clone git://opencircuitdesign.com/open_pdks
cd open_pdks

# Configure the build. A --prefix option can be given to install
# in a different place. By default after installation a 
# /usr/local/share/pdk directory is created if no --prefix is provided.
# Example for custom installation directory:
# ./configure --enable-sky130-pdk --prefix=/home/username/share/pdk

# Do the following steps one at a time and ensure no errors are
# reported after each step.
./configure --enable-sky130-pdk 
make
sudo make install
```

**8.2. Instalación de Xyce**

Xyce es un simulador de circuitos paralelo de alto rendimiento, útil para simulaciones analógicas avanzadas.

```bash
git clone https://github.com/ChipFlow/Xyce-build.git
cd Xyce-build/
./build.sh 
sudo make install prefix=/usr/local
```

**Uso de Xyce:**
```bash
mpirun -np <# procs> Xyce [options] <netlist filename>
```

**Recursos adicionales:**
- RISC-V Python Model: https://pypi.org/project/riscv-model/#files

---

## 5. Implementation & Practical Flow / Implementación y Flujo Práctico

Esta sección describe el flujo práctico de implementación del FemtoRV siguiendo el **ASIC Flow** descrito en la Sección 2. El proceso comienza con la verificación funcional del diseño RTL mediante simulación.

### 5.1. Estructura del Proyecto

El repositorio contiene la carpeta principal `femtoRV_ASIC_Flow/`, organizada de la siguiente manera:

```
femtoRV_ASIC_Flow/
├── sim/                      # Directorio de simulación
│   ├── cores/                # Modelos de simulación
│   │   ├── sim_spi_flash/    # Modelo de memoria flash SPI
│   │   └── sim_spi_ram/      # Modelo de memoria RAM SPI
│   ├── src/                  # Código fuente RTL
│   │   ├── femto.v           # Top level del diseño
│   │   ├── femtorv32_quark.v # Core RISC-V
│   │   ├── perip_uart.v      # Periférico UART
│   │   ├── uart.v            # Módulo UART
│   │   ├── MappedSPIFlash.v  # Interfaz SPI Flash
│   │   └── MappedSPIRAM.v    # Interfaz SPI RAM
│   ├── tt_um_femto_TB.v      # Testbench principal
│   ├── firmware.hex          # Firmware compilado
│   └── tt_um_femto_sim_verilog_2.gtkw  # Configuración GTKWave
└── firmware/                 # Directorio de firmware
    └── asm/                  # Código ensamblador y C
```

### 5.2. Functional Verification (Paso 3 del Frontend)

Esta etapa corresponde al **paso 3** del flujo Frontend descrito en la Sección 2.1: **Verificación Funcional**. El objetivo es simular el RTL para asegurar que el procesador ejecuta las instrucciones correctamente.

#### 5.2.1. Generación del Firmware

Antes de simular el procesador, es necesario generar el **firmware** que será ejecutado por el FemtoRV. Este firmware se compila en formato `.hex` para ser cargado en la memoria del procesador.

**Ubicación:** `femtoRV_ASIC_Flow/firmware/asm/`

**Componentes del Firmware:**
- `calculator.c` - Programa principal (calculadora)
- `bin_to_bcd.c`, `mult.c`, `div.c` - Operaciones matemáticas
- `putchar.c`, `getchar.c` - Funciones de I/O UART
- `wait.c` - Funciones de temporización
- `bram.ld` - Linker script para mapa de memoria

**Toolchain Requerido:**
```bash
# Toolchain RISC-V de 32 bits
export PATH="/opt/riscv32/bin:$PATH"

# Verificar instalación
command -v riscv32-unknown-elf-ld
riscv32-unknown-elf-ld --version
```

**Proceso de Compilación:**

El Makefile automatiza la compilación cruzada del firmware:

```makefile
# Variables del toolchain
CROSS   = riscv32-unknown-elf
CC      = $(CROSS)-gcc
AS      = $(CROSS)-as
LD      = $(CROSS)-ld
OBJCOPY = $(CROSS)-objcopy
AFLAGS  = -march=rv32i -mabi=ilp32
```

**Comandos de compilación:**

```bash
cd femtoRV_ASIC_Flow/firmware/asm/

# Compilar todos los archivos .c y .S
make

# Esto genera:
# - firmware.elf      (ejecutable linkado)
# - firmware.bin      (binario)
# - firmware.hex      (formato hexadecimal para simulación)
# - firmware_flash.hex (formato para flash)
# - firmware.lst      (listado ensamblador)
# - firmware.map      (mapa de memoria)
```

El archivo `firmware.hex` es copiado automáticamente al directorio `sim/` para ser usado en la simulación.

**Notas importantes:**
- El linker script `bram.ld` define el mapa de memoria del procesador
- Se utiliza la herramienta `firmware_words` para convertir el ELF a formato hex compatible
- La compilación usa `-march=rv32i` (arquitectura RISC-V de 32 bits, set de instrucciones base)
- Memoria RAM configurada: 16384 bytes (16 KB)

#### 5.2.2. Simulación con Icarus Verilog

Una vez generado el firmware, se procede con la simulación RTL usando **Icarus Verilog** (iverilog) y **GTKWave**.

**Ubicación:** `femtoRV_ASIC_Flow/sim/`

**Archivos de Simulación:**

| Archivo | Descripción |
|---------|-------------|
| `tt_um_femto_TB.v` | Testbench principal que instancia el diseño completo |
| `firmware.hex` | Firmware compilado para ejecución |
| `tt_um_femto_sim_verilog_2.gtkw` | Configuración de visualización de ondas |
| `cores/sim_spi_flash/spiflash.v` | Modelo de comportamiento de memoria Flash |
| `cores/sim_spi_ram/spiram.v` | Modelo de comportamiento de memoria RAM |

**Proceso de Simulación:**

El Makefile automatiza el proceso completo:

```bash
cd femtoRV_ASIC_Flow/sim/

# Ejecutar simulación completa
make sim
```

**Detalles del proceso:**

```makefile
# 1. Limpiar archivos previos
rm -f a.out *.vcd

# 2. Compilar con iverilog
iverilog -DBENCH -DSIM -DPASSTHROUGH_PLL \
         -DBOARD_FREQ=27 -DCPU_FREQ=27 \
         tt_um_femto_TB.v ${OBJS} ${SIM_OBJS}

# 3. Ejecutar simulación con vvp
vvp a.out

# 4. Visualizar resultados con GTKWave
gtkwave tt_um_femto_TB.vcd
```

**Macros de Compilación:**
- `-DBENCH`: Habilita modo banco de pruebas
- `-DSIM`: Activa características específicas de simulación
- `-DPASSTHROUGH_PLL`: PLL en modo bypass
- `-DBOARD_FREQ=27`: Frecuencia del board de 27 MHz
- `-DCPU_FREQ=27`: Frecuencia de CPU de 27 MHz

**Archivos RTL Incluidos:**
```makefile
OBJS = src/femto.v              # Top level
OBJS+= src/femtorv32_quark.v    # Core RISC-V
OBJS+= src/perip_uart.v         # Periférico UART
OBJS+= src/uart.v               # Controlador UART
OBJS+= src/MappedSPIFlash.v     # Interfaz Flash
OBJS+= src/MappedSPIRAM.v       # Interfaz RAM

SIM_OBJS = cores/sim_spi_flash/spiflash.v  # Modelo Flash
SIM_OBJS+= cores/sim_spi_ram/spiram.v      # Modelo RAM
```

#### 5.2.3. Visualización y Análisis con GTKWave

GTKWave permite visualizar las señales de simulación y verificar el comportamiento del procesador.

**Cargar configuración guardada:**
```bash
gtkwave tt_um_femto_TB.vcd tt_um_femto_sim_verilog_2.gtkw
```

El archivo `.gtkw` contiene una configuración previa con las señales más relevantes organizadas:
- Señales de reloj y reset
- Bus de instrucciones y datos
- Señales UART (TX/RX)
- Interfaces SPI (Flash y RAM)
- Estado interno del procesador

**Verificación durante la simulación:**

Durante la simulación se debe verificar:
1. ✅ El procesador inicia correctamente tras el reset
2. ✅ Las instrucciones se fetch desde la memoria correctamente
3. ✅ La ALU ejecuta operaciones matemáticas
4. ✅ La UART transmite y recibe datos
5. ✅ Los accesos a memoria SPI funcionan correctamente
6. ✅ El firmware se ejecuta sin bloqueos

**Captura de simulación GTKWave:**

![Simulación GTKWave del FemtoRV](Documents/SIM/GTKWAVE.png)
*Simulación funcional del procesador FemtoRV ejecutando el firmware de calculadora. Se observan las señales de reloj, contador de programa,y comunicación UART.*

---

### 5.3. Siguientes Pasos del Flujo

Una vez completada y verificada la simulación funcional, el diseño está listo para continuar con:

- **Logic Synthesis** (Paso 4 del Frontend) → Conversión del RTL a netlist
- **Logic Verification** (Paso 5 del Frontend) → Verificación post-síntesis
- **Physical Design** (Backend completo) → Implementación física del chip

Estas etapas se describirán en las siguientes secciones del documento.
prueba
---