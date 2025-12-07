########################################################################################################
##########     !!!!  IMPORTANTE     !!!!!                                                          #####
#             XYCE NO SOPORTA LEVEL 3                                                              #####
# Se debe modificar el archivo:                                                                       #
# /usr/local/share/pdk/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__diode_pw2nd_05v5.model.spice #
# colocando un comentario en la línea:                                                                #
# *+ level = 3.0                                                                                      #
########################################################################################################
########################################################################################################


TARGET=mult_4
TOP=mult_4
NPROC=4



all: tim_to_pwl xyce_tim plot


xyce_tim:
	mpirun -np ${NPROC} Xyce tt_um_${TARGET}.cir

extract:
	magic -T /home/linux/.volare/sky130A/libs.tech/magic/sky130A.tech tt_um_${TARGET}.gds

tim_to_pwl:
	python tim_to_cir.py tt_um_${TARGET}.tim
plot:
	python plot_mult.py 

clean:
	rm -rf *.out *.vcd *.svg *.json *.raw *.cir
