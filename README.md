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

A continuación se detallan los comandos para configurar el entorno en Ubuntu.

# Open Source ASIC Flow Tools Setup

#### 1. Yosys
Framework para síntesis Verilog-RTL.

```bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
sudo apt install make
sudo apt-get install build-essential clang bison flex     libreadline-dev gawk tcl-dev libffi-dev git     graphviz xdot pkg-config python3 libboost-system-dev     libboost-python-dev libboost-filesystem-dev zlib1g-dev
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
Simulador SPICE de código abierto.

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
Verificador de timing estático.

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
Herramienta de layout y DRC.

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
echo "deb [arch=amd64 signed-by=/usr/share-keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

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

#### 8. PDKs
Google/SkyWater SKY130  
https://github.com/google/skywater-pdk  

OpenPDK  
https://github.com/The-OpenROAD-Project/OpenPDK  

#### 9. Referencias
YOSYS, Icarus Verilog, GTKWave, Ngspice, OPENSTA, OpenLane, OpenPDK
