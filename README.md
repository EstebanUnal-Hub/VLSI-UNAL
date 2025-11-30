# VLSI-UNAL
# Implementación Física de FemtoRV: Flujo de Diseño ASIC

Este repositorio documenta el proceso completo de diseño, síntesis e implementación física (RTL-to-GDSII) del núcleo **FemtoRV**, un procesador minimalista basado en la arquitectura RISC-V. El objetivo de este proyecto es llevar una descripción de hardware (HDL) hasta un layout listo para fabricación, siguiendo los estándares de la industria VLSI.

## 1. Arquitectura del Procesador (FemtoRV)

El FemtoRV es un núcleo RISC-V diseñado para ser extremadamente ligero y fácil de entender. Antes de iniciar el flujo físico, es crucial entender la microarquitectura que estamos implementando.

El siguiente diagrama de bloques ilustra la organización interna del procesador, incluyendo la ALU, el banco de registros, el decodificador de instrucciones y las interfaces de memoria:

![Diagrama de Bloques FemtoRV](ruta/a/tu_diagrama_de_bloques_femtorv.png)
*(Reemplaza esta ruta con la imagen de tu diagrama de bloques)*

---

## 2. Flujo de Diseño VLSI (ASIC Flow)

Para materializar el FemtoRV en silicio, se siguió un flujo de diseño riguroso dividido en dos grandes etapas: **Frontend** (Diseño Lógico) y **Backend** (Diseño Físico). A continuación, se detalla cada fase apoyada en la teoría estándar de VLSI.

### Fase 1: Diseño Lógico y Funcional (Frontend)

Esta etapa se centra en la descripción del comportamiento del procesador y su traducción a compuertas lógicas digitales.

![Flujo de Diseño Lógico](ruta/a/VLSI_design_flow1.png)
*(Diagrama de referencia: Flujo Lógico y Funcional)*

Basado en el diagrama anterior, los pasos ejecutados fueron:

1.  **System Specification & Architectural Design (Especificación):**
    * Se definieron los requisitos del FemtoRV (set de instrucciones RV32I/E, frecuencia objetivo, área estimada).
2.  **RTL Description / HDL (Diseño RTL):**
    * Escritura del código en Verilog/SystemVerilog que describe el comportamiento del hardware.
3.  **Functional Verification (Verificación Funcional):**
    * Simulación del RTL para asegurar que el procesador ejecuta las instrucciones correctamente (ej. sumas, saltos, accesos a memoria) antes de pasar a la síntesis.
4.  **Logic Synthesis (Síntesis Lógica):**
    * Uso de herramientas de síntesis para transformar el código RTL (leíble por humanos) en un **Gate Level Netlist** (lista de compuertas genéricas).
5.  **Logic Verification (Verificación Lógica):**
    * Validación de que el Netlist sintetizado sigue cumpliendo con la funcionalidad original.

---

### Fase 2: Diseño Físico (Backend)

Una vez obtenidas las compuertas lógicas, el siguiente reto es colocarlas físicamente en el área del chip y conectarlas. Esta fase convierte el concepto abstracto en geometría real.

![Flujo de Diseño Físico](ruta/a/VLSI_design_flow2.png)
*(Diagrama de referencia: Flujo de Diseño Físico)*

Siguiendo el flujo detallado en la imagen, el proceso backend consta de:

1.  **Partitioning & Chip Planning (Planificación):**
    * Definición del **Floorplan**: tamaño del die, ubicación de los pines de entrada/salida (I/O) y creación de la red de alimentación (Power Delivery Network).
2.  **Placement (Colocación):**
    * Las celdas estándar (AND, OR, Flip-Flops) generadas en la síntesis se colocan automáticamente en las filas del floorplan, optimizando para reducir la longitud de los cables.
3.  **Clock Tree Synthesis - CTS (Síntesis del Árbol de Reloj):**
    * Inserción de buffers e inversores para distribuir la señal de reloj (Clock) a todos los elementos secuenciales del FemtoRV de manera sincronizada, minimizando el *skew*.
4.  **Signal Routing (Enrutado):**
    * Conexión física de todas las celdas mediante capas de metal, siguiendo las reglas de diseño (DRC) para evitar cortocircuitos.
5.  **Timing Closure (Cierre de Tiempos):**
    * Análisis Estático de Tiempo (STA) para garantizar que el chip funcione a la frecuencia deseada sin violaciones de *Setup* o *Hold*.
6.  **Physical Verification & Signoff (Verificación Final):**
    * **DRC:** Verificación de reglas de diseño (geometría correcta).
    * **LVS:** Layout vs Schematic (el dibujo coincide con el netlist).
    * Generación final del archivo **GDSII** para fabricación (Fabrication).

---

## 3. Herramientas y Entorno (Environment Setup)

*(Esta sección se completará en el siguiente paso, aquí detallaremos las versiones de software como OpenLane, Yosys, etc.)*

## 4. Instalación y Uso

*(Instrucciones para reproducir el flujo)*