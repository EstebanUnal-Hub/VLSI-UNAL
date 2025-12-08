//Darle permisos a la carpeta donde esta el pdk
sudo chown -R $USER:$USER /home/linux/.ciel
make pdk

make mount



./flow.tcl -design femto -init_design_config -add_to_designs
./flow.tcl -design femto

//Dentro del fento en OpenLane hay un .json subir el clock si sale un error
//ejemplo
{
    "DESIGN_NAME": "femto",
    "VERILOG_FILES": "dir::src/*.v",
    "CLOCK_PORT": "clk",
    "CLOCK_PERIOD": 30.0,
    "DESIGN_IS_CORE": true,
    "PL_RESIZER_HOLD_FIX": 1,
    "PL_RESIZER_TIMING_OPTIMIZATIONS": 1,
    "CTS_HOLD_FIX": 1,
    "FP_PDN_VOFFSET": 20,
    "FP_PDN_HOFFSET": 20,
    "FP_TAPCELL_DIST": 13
}


./flow.tcl -design <design name> -tag full_guide -overwrite 


En magi
//depronto esto no
export PDK_ROOT=/home/linux/.volare           # o la ruta real de tu PDK
cd ~/OpenLane/designs/femto/runs/RUN_2025.09.29_01.01.07/results/final/mag
magic -T $PDK_ROOT/sky130A/libs.tech/magic/sky130A.tech femto.mag


//esto si
cd ~/OpenLane/designs/femto/runs/RUN_2025.09.29_01.01.07/results/final/mag

# Sustituye todas las apariciones de $PDKPATH por la ruta real del PDK
sed -i 's|\$PDKPATH|/home/linux/.volare/sky130A|g' *.mag

magic -T /home/linux/.volare/sky130A/libs.tech/magic/sky130A.tech femto.mag






Extract the cir















      cuit from the layout design.
extract all
Convert the extracted circuit to SPICE model.
ext2spice cthresh 0 rthresh 0
ext2spice

pip install ltspice


compilar ngspice con:
./configure ... --enable-openmp


xyce

trilinos

https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/trilinos/12.12.1-5/trilinos_12.12.1.orig.tar.bz2



https://github.com/Xyce/Xyce/issues/103

reconfigure file:


#!/bin/sh
cSRCDIR=/Work/VLSI/Xyce-7.9/trilinos-12.12.1-Source
ARCHDIR=/usr/local/
FLAGS="-O3 -fPIC"
cmake \
-G "Unix Makefiles" \
-DCMAKE_C_COMPILER=gcc \
-DCMAKE_CXX_COMPILER=g++ \
-DCMAKE_Fortran_COMPILER=gfortran \
-DCMAKE_CXX_FLAGS="$FLAGS" \
-DCMAKE_C_FLAGS="$FLAGS" \
-DCMAKE_Fortran_FLAGS="$FLAGS" \
-DCMAKE_INSTALL_PREFIX=$ARCHDIR \
-DCMAKE_MAKE_PROGRAM="make" \
-DTrilinos_ENABLE_NOX=ON \
  -DNOX_ENABLE_LOCA=ON \
-DTrilinos_ENABLE_EpetraExt=ON \
  -DEpetraExt_BUILD_BTF=ON \
  -DEpetraExt_BUILD_EXPERIMENTAL=ON \
  -DEpetraExt_BUILD_GRAPH_REORDERINGS=ON \
-DTrilinos_ENABLE_TrilinosCouplings=ON \
-DTrilinos_ENABLE_Ifpack=ON \
-DTrilinos_ENABLE_AztecOO=ON \
-DTrilinos_ENABLE_Belos=ON \
-DTrilinos_ENABLE_Teuchos=ON \
-DTrilinos_ENABLE_COMPLEX_DOUBLE=ON \
-DTrilinos_ENABLE_Amesos=ON \
  -DAmesos_ENABLE_KLU=ON \
-DTrilinos_ENABLE_Amesos2=ON \
 -DAmesos2_ENABLE_KLU2=ON \
 -DAmesos2_ENABLE_Basker=ON \
-DTrilinos_ENABLE_Sacado=ON \
-DTrilinos_ENABLE_Stokhos=ON \
-DTrilinos_ENABLE_Kokkos=ON \
-DTrilinos_ENABLE_ALL_OPTIONAL_PACKAGES=OFF \
-DTrilinos_ENABLE_CXX11=ON \
-DTPL_ENABLE_AMD=ON \
-DAMD_LIBRARY_DIRS="/usr/lib" \
-DTPL_AMD_INCLUDE_DIRS="/usr/include/suitesparse" \
-DTPL_ENABLE_BLAS=ON \
-DTPL_ENABLE_LAPACK=ON \
$SRCDIR


--------------------------------------
chmod u+x reconfigure
./reconfigure

make
make install




https://cadhut.com/2023/05/29/how-to-install-openroad-and-other-vlsi-tools-under-ubuntu-20-04-22-04-mint-21-or-zorin-os/




https://fpga-ignite.github.io/lab-materials/OpenLaneTutorial-HardeningtheCore.pdf


************************************************************************
************************************************************************

pip3 install ltspice

En /.local/lib/python3.13/site-packages/ltspice/ltspice.py 


        with open(self.file_path, 'rb') as f:
#            if filesize > self.max_header_size:
#                data = f.read(self.max_header_size)  
#            else: