/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_mult_4 (
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
  assign uio_out[7:1] = 0;
  assign uio_oe[0] = 1'b0;   // uio[0] es ENTRADA (init)
  assign uio_oe[1] = 1'b1;   // uio[1] es SALIDA (done)
  assign uio_oe[7:2] = 6'b0; // resto sin usar, como entradas

  // input reset:
  reg resetn;
  always @(negedge clk) resetn <=rst_n;
  
  //instance
  mult_4 mult4(
    .clk(clk),
    .rst(resetn),
    .A(ui_in[3:0]),
    .B(ui_in[7:4]),
    .pp(uo_out[7:0]),
    .init(uio_in[0]),
    .done(uio_out[0])
  );



  // List all unused inputs to prevent warnings
  wire _unused = &{ena,uio_in[7:1], 1'b0};


endmodule
