TARGET=femto
TOP=femto
TINYTO_TOP=tt_um_femto
SKY_LIB_TECH=$(HOME)/.volare/sky130A/libs.tech/openlane/


OBJS = src/femto.v
OBJS+= src/femtorv32_quark.v
OBJS+= src/perip_uart.v
OBJS+= src/uart.v
OBJS+= src/MappedSPIFlash.v
OBJS+= src/MappedSPIRAM.v


SIM_OBJS = cores/sim_spi_flash/spiflash.v
SIM_OBJS+= cores/sim_spi_ram/spiram.v


BUILD_DIR = build

all: sim

sim: 
	rm -f a.out *.vcd
	iverilog -DBENCH -DSIM -DPASSTHROUGH_PLL -DBOARD_FREQ=27 -DCPU_FREQ=27 tt_um_femto_TB.v ${OBJS} ${SIM_OBJS}
	vvp a.out
	gtkwave tt_um_femto_TB.vcd



clean:
	rm -rf impl obj_dir *svg a.out *.vcd *.json *.bit build *.vpp *.log SOC_flash_synth_sky SOC_flash_synth_sky.v ${OPENLANE_TOP}.vsky130_fd_sc_hd__blackbox.v


