########################################################################################################
##########     !!!!  IMPORTANTE     !!!!!                                                          #####
#             XYCE NO SOPORTA LEVEL 3                                                              #####
# Se debe modificar el archivo:                                                                       #
# /usr/local/share/pdk/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__diode_pw2nd_05v5.model.spice #
# colocando un comentario en la línea:                                                                #
# *+ level = 3.0                                                                                      #
########################################################################################################
########################################################################################################


TARGET=femto
TOP=femto
NPROC=4



all: xyce_tim

extract:
	magic -T /home/linux/.volare/sky130A/libs.tech/magic/sky130A.tech tt_um_${TARGET}.gds

xyce_tim:
	mpirun -np ${NPROC} Xyce tt_um_${TARGET}.cir

clean:
	rm -rf *.out *.vcd *.svg *.json *.raw *.cir
