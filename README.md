# FemtoRV Physical Implementation: ASIC Flow / Implementación Física de FemtoRV

Este repositorio documenta el proceso completo de diseño, síntesis e implementación física (RTL-to-GDSII) del núcleo **FemtoRV**, un procesador minimalista basado en la arquitectura RISC-V. El objetivo de este proyecto es llevar una descripción de hardware (HDL) hasta un layout listo para fabricación.

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

1.  **System Specification & Architectural Design (Especificación):** Definición de requisitos del FemtoRV.
2.  **RTL Description / HDL (Diseño RTL):** Escritura del código en Verilog.
3.  **Functional Verification (Verificación Funcional):** Simulación del RTL para asegurar que el procesador ejecuta las instrucciones correctamente.
4.  **Logic Synthesis (Síntesis Lógica):** Transformación del código RTL a un *Gate Level Netlist*.
5.  **Logic Verification (Verificación Lógica):** Validación del Netlist.

### 2.2. Physical Design (Backend) / Diseño Físico
Una vez obtenidas las compuertas lógicas, el siguiente reto es colocarlas físicamente en el área del chip.

![Physical Design Flow](Documents/ASIC Flow/VLSI_design_flow2.png)
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

*(Próxima sección a completar...)*