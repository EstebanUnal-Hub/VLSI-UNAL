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


xyce_tim:
	mpirun -np ${NPROC} Xyce ${TARGET}.cir


clean:
	rm -rf *.out *.vcd *.svg *.json *.raw *.cir
