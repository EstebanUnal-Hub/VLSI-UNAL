module lsr (clk , in_A , shift , load , s_A);
  input clk;
  input [3:0]in_A;
  input load;
  input shift;
  output reg [7:0]s_A;

always @(negedge clk)
  if(load)
     s_A = in_A ;
  else
   begin
    if(shift) s_A = s_A << 1 ;
    else  s_A = s_A;
   end

endmodule
