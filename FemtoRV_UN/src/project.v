/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_femto (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  
  assign uio_out = 0;
  assign uio_oe  = 0;

  /* verilator lint_off SYNCASYNCNET */
  reg resetn;
  /* verilator lint_on SYNCASYNCNET */
  always @(negedge clk) resetn <= rst_n;

  femto femto0(
    .clk(clk),
    .resetn(resetn),
    .spi_mosi(uo_out[0]),
    .spi_mosi_ram(uo_out[1]),
    .spi_cs_n(uo_out[2]),
    .spi_cs_n_ram(uo_out[3]),
    .spi_clk_ram(uo_out[4]),
    .spi_clk(uo_out[5]),
    .LEDS(uo_out[6]),
    .TXD(uo_out[7]),

    .spi_miso(ui_in[0]),
    .spi_miso_ram(ui_in[1]),
    .RXD(ui_in[2])
  );


  // List all unused inputs to prevent warnings
  wire _unused = &{ena,uio_in[7:0],ui_in[7:3], 1'b0};

endmodule
