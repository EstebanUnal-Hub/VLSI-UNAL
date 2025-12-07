# 4-Bit Sequential Multiplier

## Overview
this project was created by Esteban UNAL
This project implements a **4-bit sequential multiplier** using the shift-and-add algorithm. The design multiplies two 4-bit unsigned numbers (A and B) to produce an 8-bit product (PP). The multiplier operates sequentially, performing one bit operation per clock cycle, making it area-efficient for ASIC implementation.

## How It Works

The multiplier uses the **shift-and-add algorithm**:

1. **Initialization**: When `init` is asserted, the multiplier loads operands A and B into internal shift registers and resets the accumulator.

2. **Sequential Operation**: On each clock cycle:
   - The LSB (Least Significant Bit) of B is examined
   - If LSB = 1, operand A is added to the accumulator
   - Both operands are shifted right by one position
   - The process repeats until B becomes zero

3. **Completion**: The `done` signal indicates when the multiplication is complete and the result is ready.

## Architecture

The design consists of five main components:

- **RSR (Right Shift Register)**: Shifts operand B right, examining one bit per cycle
- **LSR (Left Shift Register)**: Shifts operand A left for proper alignment during addition
- **ACC (Accumulator)**: Accumulates partial products to generate the final result
- **COMP (Comparator)**: Detects when B reaches zero (multiplication complete)
- **Control Unit**: FSM that orchestrates the multiplication sequence

## Timing

The multiplication takes **4-5 clock cycles** depending on the operand values:
- Minimum: 4 cycles (when B has trailing zeros)
- Maximum: 5 cycles (worst case)

## Pin Configuration

### Inputs (ui)
- `ui[3:0]`: Operand A (4-bit multiplicand)
- `ui[7:4]`: Operand B (4-bit multiplier)

### Outputs (uo)
- `uo[7:0]`: PP - Product output (8-bit result)

### Bidirectional (uio)
- `uio[0]`: init - Start multiplication (input)
- `uio[1]`: done - Multiplication complete flag (output)

## Usage Example

1. Apply operands A and B to input pins
2. Assert `init` signal (high pulse) to start multiplication
3. Wait for `done` signal to go high
4. Read 8-bit result from `PP` output

**Example**: A=5 (0101), B=3 (0011) → PP=15 (00001111)

## Test Sequence