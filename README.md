# FemtoRV Physical Implementation: ASIC Flow

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![RISC-V](https://img.shields.io/badge/ISA-RISC--V-orange.svg)](https://riscv.org/)
[![Tiny Tapeout](https://img.shields.io/badge/Platform-Tiny%20Tapeout-green.svg)](https://tinytapeout.com)

Este repositorio documenta el proceso completo de diseño, síntesis e implementación física (RTL-to-GDSII) del núcleo **FemtoRV**, un procesador basado en la arquitectura RISC-V. El objetivo de este proyecto es llevar una descripción de hardware (HDL) hasta un layout listo para fabricación utilizando **Tiny Tapeout**.

*This repository documents the complete design, synthesis, and physical implementation (RTL-to-GDSII) process of the **FemtoRV** core, a RISC-V based processor. The goal is to take an HDL description to a fabrication-ready layout using **Tiny Tapeout**.*

---

## 📑 Tabla de Contenidos / Table of Contents

1. [Arquitectura del Procesador](#1-processor-architecture--arquitectura-del-procesador)
2. [Flujo de Diseño VLSI](#2-vlsi-design-flow--flujo-de-diseño-vlsi)
3. [Plataforma de Fabricación](#3-fabrication-platform--plataforma-de-fabricación)
4. [Herramientas y Entorno](#4-tools--environment--herramientas-y-entorno)
5. [Guía de Instalación](#5-installation-guide--guía-de-instalación)
6. [Recursos Adicionales](#6-additional-resources--recursos-adicionales)

---

## 1. Processor Architecture / Arquitectura del Procesador

El **FemtoRV** es un núcleo RISC-V diseñado para ser extremadamente ligero y fácil de entender, ideal para aplicaciones educativas y proyectos de hardware de código abierto.

*The **FemtoRV** is a RISC-V core designed to be extremely lightweight and easy to understand, ideal for educational applications and open-source hardware projects.*

### Características Principales / Key Features

- ✅ Arquitectura RISC-V RV32I
- ✅ Diseño minimalista y altamente optimizado
- ✅ Compatible con el flujo de diseño open-source
- ✅ Documentación completa del proceso RTL-to-GDSII

![FemtoRV Block Diagram](ruta/a/tu_diagrama_de_bloques_femtorv.png)
*Diagrama de bloques del procesador FemtoRV / FemtoRV processor block diagram*

---

## 2. VLSI Design Flow / Flujo de Diseño VLSI

El flujo de diseño ASIC se divide en dos etapas principales: **Frontend** (diseño lógico) y **Backend** (diseño físico).

*The ASIC design flow is divided into two main stages: **Frontend** (logic design) and **Backend** (physical design).*

### 2.1. Frontend: Logic & Functional Design

Etapa centrada en la descripción del comportamiento del procesador y su verificación funcional.

![Logical Design Flow](Documents/ASIC_Flow/VLSI_design_flow1.png)

**Pasos del Frontend / Frontend Steps:**

1. **System Specification** - Definición de requisitos y especificaciones
2. **RTL Description** - Implementación en Verilog
3. **Functional Verification** - Simulación y validación del comportamiento
4. **Logic Synthesis** - Conversión de RTL a netlist de compuertas
5. **Logic Verification** - Validación del netlist sintetizado

### 2.2. Backend: Physical Design

Etapa enfocada en la implementación física del diseño en silicio.

![Physical Design Flow](Documents/ASIC_Flow/VLSI_design_flow2.png)

**Pasos del Backend / Backend Steps:**

1. **Floorplanning** - Planificación del área y definición de pines
2. **Placement** - Ubicación óptima de celdas estándar
3. **Clock Tree Synthesis (CTS)** - Construcción del árbol de distribución de reloj
4. **Routing** - Conexión física de todas las celdas
5. **Timing Closure** - Verificación de tiempos (setup/hold)
6. **Physical Verification** - DRC, LVS y generación del GDSII final

---

## 3. Fabrication Platform / Plataforma de Fabricación

### 🔧 Tiny Tapeout

![Tiny Tapeout Logo](https://tinytapeout.com/tt_logo.png)

> **Tiny Tapeout** es un proyecto educativo que facilita y abarata la fabricación de diseños digitales y analógicos en chips reales.

> *Tiny Tapeout is an educational project that makes it easier and cheaper to manufacture digital and analog designs on real chips.*

🔗 **Más información:** [tinytapeout.com](https://tinytapeout.com)

### Plantilla del Proyecto / Project Template

Este proyecto utiliza la **plantilla oficial de Tiny Tapeout**, que proporciona:

- Configuración preconfigurada de OpenLane
- Restricciones de pines y área definidas
- Integración con GitHub Actions para CI/CD
- Compatibilidad con el shuttle de fabricación

**Repositorio:** [`EstebanUnal-Hub/VLSI-UNAL`](https://github.com/EstebanUnal-Hub/VLSI-UNAL)

---

## 4. Tools & Environment / Herramientas y Entorno

### Requisitos del Sistema / System Requirements

- **OS:** Ubuntu 20.04 LTS o superior
- **RAM:** Mínimo 8GB (recomendado 16GB)
- **Disco:** Mínimo 50GB de espacio libre
- **Procesador:** x86_64 compatible

### Herramientas Utilizadas / Tools Used

| Herramienta | Función | Etapa |
|-------------|---------|-------|
| **OpenLane** | Automatización del flujo RTL-to-GDSII | Frontend + Backend |
| **Yosys** | Síntesis lógica | Frontend |
| **Icarus Verilog** | Simulación RTL | Frontend |
| **GTKWave** | Visualización de ondas | Frontend |
| **OpenSTA** | Análisis estático de tiempo | Backend |
| **Magic VLSI** | Visualización de layout y DRC | Backend |
| **Ngspice** | Simulación SPICE | Verificación |
| **SKY130 PDK** | Process Design Kit | Backend |

---

## 5. Installation Guide / Guía de Instalación

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/EstebanUnal-Hub/VLSI-UNAL.git
cd VLSI-UNAL

# Ejecutar script de instalación (si está disponible)
./install_tools.sh
```

### Instalación Manual

#### 5.1. Yosys

Framework para síntesis Verilog-RTL.

```bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
sudo apt install make build-essential clang bison flex libreadline-dev \
    gawk tcl-dev libffi-dev git graphviz xdot pkg-config python3 \
    libboost-system-dev libboost-python-dev libboost-filesystem-dev zlib1g-dev
make config-gcc
make
sudo make install
```

#### 5.2. Icarus Verilog

Compilador Verilog que genera netlists.

```bash
sudo apt install iverilog
```

#### 5.3. GTKWave

Visualizador de ondas compatible con VCD.

```bash
sudo apt install gtkwave
```

#### 5.4. ngspice

Simulador SPICE de código abierto para circuitos eléctricos y electrónicos.

```bash
sudo apt install build-essential libxaw7-dev
tar -zxvf ngspice-40.tar.gz
cd ngspice-40
mkdir release && cd release
../configure --with-x --with-readline=yes --disable-debug
make
sudo make install
```

#### 5.5. OpenSTA

Verificador de timing estático.

```bash
sudo apt install cmake clang gcc tcl swig bison flex
git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA
mkdir build && cd build
cmake ..
make
sudo make install
```

#### 5.6. Magic VLSI

Herramienta de layout desarrollada en UC Berkeley.

```bash
sudo apt install m4 tcsh csh libx11-dev tcl-dev tk-dev libcairo2-dev \
    mesa-common-dev libglu1-mesa-dev libncurses-dev
git clone https://github.com/RTimothyEdwards/magic
cd magic
./configure
make
sudo make install
```

#### 5.7. Docker & OpenLane

Flujo completo RTL-to-GDSII.

```bash
# Instalar Docker
sudo apt update && sudo apt upgrade
sudo apt install build-essential python3 python3-venv python3-pip make git
sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Configurar permisos
sudo groupadd docker
sudo usermod -aG docker $USER

# Instalar OpenLane
cd ~
git clone https://github.com/The-OpenROAD-Project/OpenLane
cd OpenLane
make
make test
```

#### 5.8. SKY130 PDK

Process Design Kit de SkyWater 130nm.

```bash
git clone git://opencircuitdesign.com/open_pdks
cd open_pdks
./configure --enable-sky130-pdk
make
sudo make install
```

#### 5.9. Xyce (Opcional)

Simulador paralelo de circuitos.

```bash
git clone https://github.com/ChipFlow/Xyce-build.git
cd Xyce-build
./build.sh
sudo make install prefix=/usr/local

# Uso:
# mpirun -np <# procs> Xyce [options] <netlist filename>
```

---

## 6. Additional Resources / Recursos Adicionales

### Documentación

- 📖 [RISC-V Specification](https://riscv.org/technical/specifications/)
- 📖 [OpenLane Documentation](https://openlane.readthedocs.io/)
- 📖 [SKY130 PDK Documentation](https://skywater-pdk.readthedocs.io/)
- 📖 [Tiny Tapeout Guide](https://tinytapeout.com/guides/)

### Comunidad

- 💬 [RISC-V Forum](https://groups.google.com/a/groups.riscv.org/g/sw-dev)
- 💬 [Tiny Tapeout Discord](https://discord.gg/tinytapeout)
- 💬 [OpenLane Discussions](https://github.com/The-OpenROAD-Project/OpenLane/discussions)

#