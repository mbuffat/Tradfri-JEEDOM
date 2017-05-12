#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# programme acces pont TRADFRI
# M. BUFFAT 2017

# allume ou eteind des lumieres avec intensité

import sys
import pytradfri
import time
import configparser
#
# lecture configuration dans tradfri.cfg
#
conf = configparser.ConfigParser()
# repertoire courant ou dans /etc
conf.read(['tradfri.cfg','/etc/tradfri.cfg'])
# pont tradfri
IP     = conf.get('IKEA','IP')
KEY    = conf.get('IKEA','KEY')

# configuration variables. 
api = pytradfri.coap_cli.api_factory(IP, KEY)
gateway = pytradfri.gateway.Gateway(api)
# recuperation info
devices = gateway.get_devices()
lights = [dev for dev in devices if dev.has_light_control]
#
if (len(sys.argv) == 1):
    print("\nsyntaxe: set_tradfri [on/off/dim] [val] ampoules_id\n")
    print("\t\tPont TRADFRI ip:",IP)
    print("\n\tdevices %d"%len(devices))
    print(devices)
    # Print all lights
    print("\n\tliste des ampoules %d"%len(lights))
    print(lights,"\n")
    sys.exit(0)
# allume ou eteinds les ampoules
dim = None
state = None
ampoulesId = None
if sys.argv[1] == "dim" :
    dim = int(sys.argv[2])
    ampoulesId = [int(sys.argv[k]) for k in range(3,len(sys.argv))]
elif sys.argv[1] == "on" :
    state= True
    ampoulesId = [int(sys.argv[k]) for k in range(2,len(sys.argv))]
else:
    state= False
    ampoulesId = [int(sys.argv[k]) for k in range(2,len(sys.argv))]
#
for ampoule in ampoulesId :
   print("Etat ampoule %d"%(ampoule))
   # device
   for light in lights:
        if light.id == ampoule :
            Light = light.light_control.lights[0]
            break
   # ampoule associée
   # change etat
   if dim!= None :
        Light.device.light_control.set_dimmer(dim)
   else:
        Light.device.light_control.set_state(state)
   Light.device.update()
   print("name ",Light.device.name)
   print("state ",Light.state)
   print("dimmmer ",Light.dimmer)
#
sys.exit(0)
