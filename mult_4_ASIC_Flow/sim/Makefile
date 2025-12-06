DESIGN          = mult_4

IVERILOG        = iverilog

SRC             = $(DESIGN).v src/rsr.v src/lsr.v src/acc.v src/control_mult.v src/comp.v \

SIM_SRC = $(DESIGN)_TB.v          \



 
all:            iversim



clean:
	rm -f *~ */*~ a.out *.log *.key *.edf *.ps trace.dat  mult_32_synth_sky.v
	rm -f *.bit *.json


iversim:  build/project.src
	$(IVERILOG) -o simulation/$(DESIGN)_TB.vvp $(VINCDIR) $(SRC) $(SIM_SRC) -s $(DESIGN)_TB
	vvp simulation/$(DESIGN)_TB.vvp; mv $(DESIGN)_TB.vcd simulation/
	gtkwave simulation/$(DESIGN)_TB.vcd&
	


	