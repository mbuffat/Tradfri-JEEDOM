#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# programme acces pont TRADFRI
# M. BUFFAT 2017

# allume ou eteind des lumieres avec intensité

import sys
import time
import configparser

from pytradfri import Gateway
from pytradfri.api.libcoap_api import api_factory

DEBUG=False
# parametres
pos=1
if len(sys.argv)>1 and sys.argv[pos] == "-d": 
    DEBUG=True
    pos += 1
#
# lecture configuration dans tradfri.cfg
#
conf = configparser.ConfigParser()
# repertoire courant ou dans /etc
conf.read(['tradfri.cfg','/etc/tradfri.cfg'])
# pont tradfri
IP     = conf.get('IKEA','IP')
KEY    = conf.get('IKEA','KEY')
# couleurs en hexa
COL={'warm':'efd275','normal':'f1e0b5','cold':'f5faf6'}

# configuration API IKEA
api     = api_factory(IP, KEY)
gateway = Gateway()

# recuperation des lampes
devices_command  = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(*devices_commands)
if DEBUG: print("devices:",devices)
lights = [dev for dev in devices if dev.has_light_control]
if DEBUG: print("lights:",lights)
# et des taches
tasks_command = gateway.get_smart_tasks()
tasks = api(tasks_command)

# syntaxe
if (len(sys.argv) == 1):
    print("\nsyntaxe: set_tradfri [-d] [on/off/status/dim/col] [val/cold/normal/warm] ampoules_id\n")
    print("\t\tPont TRADFRI ip:",IP)
    print("\n\tdevices %d"%len(devices))
    print(devices)
    # Print all lights
    print("\n\tliste des ampoules %d"%len(lights))
    print(lights,"\n")
    sys.exit(0)

# allume ou eteinds les ampoules
dim   = None
state = None
color = None
ampoulesId = None

if sys.argv[pos] == "dim" :
    dim = int(sys.argv[pos+1])
    ampoulesId = [int(sys.argv[k]) for k in range(pos+2,len(sys.argv))]
elif sys.argv[pos] == "col":
    color = COL[sys.argv[pos+1]]
    ampoulesId = [int(sys.argv[k]) for k in range(pos+2,len(sys.argv))]
elif sys.argv[pos] == "on" :
    state= True
    ampoulesId = [int(sys.argv[k]) for k in range(pos+1,len(sys.argv))]
elif sys.argv[pos] == "off":
    state= False
    ampoulesId = [int(sys.argv[k]) for k in range(pos+1,len(sys.argv))]
else :
    ampoulesId = [int(sys.argv[k]) for k in range(pos+1,len(sys.argv))]
#
for ampoule in ampoulesId :
   print("\tAmpoule %d"%(ampoule))
   # device
   Light =None
   for light in lights:
        if light.id == ampoule :
            Light = light
            break
   # ampoule associée
   if Light==None:
       print("ERREUR: aucune ampoulei trouvee ",Light)
       continue
   # change etat si branchee
   if Light.reachable:
        if dim!= None :
            if DEBUG: print("set dim ",dim)
            dim_command = Light.light_control.set_dimmer(dim)
            api(dim_command)
            update_command=Light.update()
            api(update_command)
        elif color != None:
            if DEBUG: print("set color ",color)
            color_command=Light.light_control.set_hex_color(color)
            api(color_command)
            update_command=Light.update()
            api(update_command)
        elif state != None:
            if DEBUG: print("set state ",state)
            state_command=Light.light_control.set_state(state)
            api(state_command)
            update_command=Light.update()
            api(update_command)
        else:
            print("name    ",Light.name)
            print("state   ",Light.light_control.lights[0].state)
            print("dimmmer ",Light.light_control.lights[0].dimmer)
            print("color   ",Light.light_control.lights[0].hex_color)
            print("reach   ",Light.reachable)
   else:
        # cas non branche
            print("Attention ampoule non branchée")
            print("name    ",Light.name)
            print("state   ",False)
            print("reach   ",Light.reachable)
#
sys.exit(0)
