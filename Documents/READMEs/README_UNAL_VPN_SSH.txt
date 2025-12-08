##################################################### VPN + SSH Access ###############################################################

*********************************************
                    Index
*********************************************

    * VPN Configuration (UNAL)
    * SSH Connection
    * Environment Setup
    * Directory Contents

*********************************************


************************************************************************************************************
                                VPN Configuration (UNAL)
************************************************************************************************************
**Install Forticlient video:
https://www.youtube.com/watch?v=h7rrkDs271c

**Configure:
- VPN Name: **UNAL**
- Username: **UNAL**
- Server URL: **https://vpnman.unal.edu.co:443**
- Customizer Port: **443**
- Prompt on Login: **Enabled**
- Client Certificate: **NONE**

➡ Once connected, use your institutional credentials to log in.


************************************************************************************************************
                                SSH Connection
************************************************************************************************************

1) **Open Terminal**
2) **Run the following command:**
   ssh -X cicamargoba@192.168.4.83
3) **Enter the password** when prompted. 
Caincito-1
4) Upon successful login, you’ll access the remote shell environment.


************************************************************************************************************
                                Environment Setup
************************************************************************************************************

1) **Navigate to the ASIC tools directory:**
   cd iic-osic-tools/

2) **Start the environment shell:**
   ./start_shell.sh
3)**change user**
   su cain
4) **List available files:**
   ls
-Directory Contents:
***
	femto.cir
	femto spice
	femto_w_c.spice
	firmware.hex
	firmware_flash.hex
	Makefile
	mult_32
	plot_femto.py
	spice_models.lib
	test_femto.gtkw
***


************************************************************************************************************
                                PATH Configuration
************************************************************************************************************

PATH variable:
export PATH=$PATH:/headless/.local/bin:/headless/.local/bin:/foss/tools/bin:/foss/tools/sak:/usr/local/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/foss/tools/kactus2:/foss/tools/klayout:/foss/tools/osic-multitool
************************************************************************************************************
                                
************************************************************************************************************

###########################################################################################################################################################


