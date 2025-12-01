# FemtoRV Physical Implementation: ASIC Flow / Implementación Física de FemtoRV

Este repositorio documenta el proceso completo de diseño, síntesis e
implementación física (RTL-to-GDSII) del núcleo **FemtoRV**, un
procesador basado en la arquitectura RISC-V. El objetivo de este
proyecto es llevar una descripción en HDL hasta un layout listo para
fabricación. Además, se utiliza **Tiny Tapeout** para realizar la
manufactura del chip.

------------------------------------------------------------------------

## 1. Processor Architecture / Arquitectura del Procesador (FemtoRV)

El FemtoRV es un núcleo RISC-V diseñado para ser extremadamente ligero y
fácil de entender. Antes de iniciar el flujo físico, es importante
comprender la microarquitectura que estamos implementando.

![FemtoRV Block Diagram](ruta/a/tu_diagrama_de_bloques_femtorv.png)
*(Reemplaza la ruta con la imagen real)*

------------------------------------------------------------------------

## 2. VLSI Design Flow / Flujo de Diseño VLSI (ASIC Flow)

El flujo completo para llevar un diseño desde RTL hasta GDSII se divide
en dos grandes etapas: **Frontend** (Diseño Lógico) y **Backend**
(Diseño Físico).

### 2.1. Logic & Functional Design (Frontend) / Diseño Lógico y Funcional

En esta etapa se describe el comportamiento del procesador y se verifica
su funcionamiento.

![Logical Design Flow](Documents/ASIC_Flow/VLSI_design_flow1.png)

Pasos realizados:

1.  **System Specification / Especificación del Sistema:** Definición de
    requisitos, entradas y salidas.
2.  **RTL Description / Diseño RTL:** Implementación del FemtoRV en
    Verilog.
3.  **Functional Verification / Verificación Funcional:** Simulación del
    RTL.
4.  **Logic Synthesis / Síntesis Lógica:** Traducción del RTL a Netlist.
5.  **Logic Verification / Verificación Lógica:** Validación del
    Netlist.

### 2.2. Physical Design (Backend) / Diseño Físico

En esta etapa se implementa físicamente el diseño en el área del chip.

![Physical Design Flow](Documents/ASIC_Flow/VLSI_design_flow2.png)

Pasos realizados:

1.  **Floorplanning:** Definición del área y pines.
2.  **Placement:** Colocación de celdas estándar.
3.  **CTS (Clock Tree Synthesis):** Construcción del árbol de reloj.
4.  **Routing / Enrutado:** Conexión eléctrica del diseño.
5.  **Timing Closure:** Validación de *setup* y *hold*.
6.  **Physical Verification:** DRC, LVS y generación de GDSII.

------------------------------------------------------------------------

## 3. Fabrication Platform / Plataforma de Fabricación

Este proyecto se fabricó mediante **Tiny Tapeout**.

### About Tiny Tapeout / Acerca de Tiny Tapeout

> Tiny Tapeout es un proyecto educativo que facilita la fabricación de
> diseños digitales y analógicos.

Más información en: [tinytapeout.com](https://tinytapeout.com)

### Project Template Usage / Uso de la Plantilla

Fue necesario emplear la plantilla oficial de Tiny Tapeout, que
proporciona:

-   Configuración de OpenLane
-   Restricciones de pines
-   Configuraciones automáticas de CI/CD

Repositorio del proyecto: `EstebanUnal-Hub/VLSI-UNAL`

------------------------------------------------------------------------

## 4. Tools & Environment / Herramientas y Entorno

Para replicar este flujo se empleó un entorno Linux. Las herramientas
utilizadas fueron:

-   **OpenLane:** Automatiza el flujo RTL-to-GDSII.
-   **Icarus Verilog & GTKWave:** Verificación funcional.
-   **Yosys:** Síntesis lógica.
-   **OpenSTA:** Análisis estático de tiempo.
-   **Magic VLSI:** Verificación física y visualización del layout.
-   **Ngspice:** Simulación eléctrica de bajo nivel.

------------------------------------------------------------------------

## Installation Guide / Guía de Instalación

### 1. Yosys

``` bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
sudo apt install make build-essential clang bison flex libreadline-dev gawk tcl-dev libffi-dev git graphviz xdot pkg-config python3 libboost-system-dev libboost-python-dev libboost-filesystem-dev zlib1g-dev
make config-gcc
make
sudo make install
```

### 2. Icarus Verilog

``` bash
sudo apt install iverilog
```

### 3. GTKWave

``` bash
sudo apt install gtkwave
```

### 4. ngspice

``` bash
sudo apt-get install build-essential libxaw7-dev
tar -zxvf ngspice-40.tar.gz
cd ngspice-40
mkdir release && cd release
../configure --with-x --with-readline=yes --disable-debug
make
sudo make install
```

### 5. OpenSTA

``` bash
sudo apt-get install cmake clang gcc tcl swig bison flex
git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA
mkdir build && cd build
cmake ..
make
sudo make install
```

### 6. Magic

``` bash
sudo apt-get install m4 tcsh csh libx11-dev tcl-dev tk-dev libcairo2-dev mesa-common-dev libglu1-mesa-dev libncurses-dev
git clone https://github.com/RTimothyEdwards/magic
cd magic
./configure
make
sudo make install
```

### 7. OpenLane & Docker

``` bash
sudo apt update && sudo apt upgrade
sudo apt install build-essential python3 python3-venv python3-pip make git
sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share-keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

sudo groupadd docker
sudo usermod -aG docker $USER
```

Instalación de OpenLane:

``` bash
cd ~
git clone https://github.com/The-OpenROAD-Project/OpenLane
cd OpenLane
make
make test
```

### 8. PDKs - SKY130

``` bash
git clone git://opencircuitdesign.com/open_pdks
cd open_pdks
./configure --enable-sky130-pdk
make
sudo make install
```

### 9. Xyce

``` bash
git clone https://github.com/ChipFlow/Xyce-build.git
cd Xyce-build
./build.sh
sudo make install prefix=/usr/local
```

------------------------------------------------------------------------