#! /usr/bin/env python3
# daemon tradfy 
import sys
import time
import socket
import json
import requests,logging
import configparser

from pytradfri import Gateway
from pytradfri.api.libcoap_api import api_factory

#
DEBUG=False
SESSION_JEEDOM=None
#
def JeedomAPI(ID="0",methode="ping"):
    HEADERS = {'content-type': 'application/json'}
    DATA = {'apikey' : API_KEY, "id": ID, }
    PARAMS = {                                                                
         "method" : methode,                                                    
         "id" : ID ,
         "jsonrpc" : "2.0",
         "params": DATA,
    }                                                                     
    response = SESSION_JEEDOM.post(URL_JEEDOM, data=json.dumps(PARAMS), headers=HEADERS)
    if not response.ok :
        print("Erreur API:",ID,methode," code:",response.status_code)
    return response
#
def JeedomCmd(ID,val=None):
    if val != None :
        DATA={"apikey" : API_KEY , "type" : 'cmd' , "id" : int(ID), "slider" : val}
    else:
        DATA={"apikey" : API_KEY , "type" : 'cmd' , "id" : int(ID), }
    response = SESSION_JEEDOM.post(URL_JEEDOM, params=DATA)
    if not response.ok :
        print("CMD:",ID,val," code:",response.status_code)
    #print(response.url)
    return response
#
# equipements JEEDOM
# =================
class EquiptJEEDOM():
    """ gestion des widgets Lumieres Jeedom"""
    def __init__(self,lumid):
        rep=JeedomAPI()
        rep.close()
        self.LumId=[int(l) for l in lumid]
        N=len(self.LumId)
        self.EtatId     = [None]*N
        self.SetOnId    = [None]*N
        self.SetOffId   = [None]*N
        self.BrightId   = [None]*N
        self.SetBrightId= [None]*N
        self.ReachId    = [None]*N
        self.SetReachId = [None]*N
        for k,lum in enumerate(self.LumId):
            reponse = JeedomAPI(lum,"eqLogic::fullById")
            rep= reponse.json()['result']['cmds']
            for cmd in rep:
                nom=cmd['name']
                # print(nom)
                if nom == "etat" :
                    self.EtatId[k] = cmd['id']
                elif nom== "on":
                    self.SetOnId[k] = cmd['id']
                elif nom== "off":
                    self.SetOffId[k] = cmd['id']
                elif nom== "bright":
                    self.BrightId[k] = cmd['id']
                elif nom== "setbright":
                    self.SetBrightId[k] = cmd['id']
                elif nom== "reach":
                    self.ReachId[k] = cmd['id']
                elif nom== "setreach":
                    self.SetReachId[k] = cmd['id']
            #reponse.close()
        # variables d'etat
        self.etat=[None]*N
        self.reach=[None]*N
        self.bright=[None]*N
        self.state()
        return
    def state(self):
        """ lecture etat """
        N=len(self.LumId)
        for k in range(N):
            # lecture etat
            reponse = JeedomAPI(self.EtatId[k],"cmd::execCmd")
            if DEBUG: print(reponse)
            rep = reponse.json()['result']
            self.etat[k]=int(rep['value'])
            #reponse.close()
            reponse = JeedomAPI(self.ReachId[k],"cmd::execCmd")
            rep = reponse.json()['result']
            self.reach[k]=int(rep['value'])
            #reponse.close()
            reponse = JeedomAPI(self.BrightId[k],"cmd::execCmd")
            rep = reponse.json()['result']
            self.bright[k]=int(rep['value'])
            #reponse.close()
        return
    def info(self):
        """ affiche etat """
        self.state()
        N=len(self.LumId)
        print("Liste des widget lumieres JEEDOM : ",N)
        for k in range(N):
            print("\tlum[%d] id: %s %s state=%d bright=%d reach=%d "
                    %(k,self.LumId[k],self.EtatId[k],self.etat[k],self.bright[k],self.reach[k]))
        return
    def set_state(self,k,on=True):
        if on :
            rep = JeedomCmd(self.SetOnId[k])
            #rep.close()
        else:
            rep = JeedomCmd(self.SetOffId[k])
            #rep.close()
        return
    def set_reach(self,k,state=True):
        if state :
            rep = JeedomCmd(self.SetReachId[k],100)
            #rep.close()
        else :
            rep = JeedomCmd(self.SetReachId[k],0)
            #rep.close()
            rep = JeedomCmd(self.SetOffId[k])
            #rep.close()
        return
    def set_bright(self,k,level=0):
        rep = JeedomCmd(self.SetBrightId[k],level)
        self.bright[k]=level
        #rep.close()
        return
#
# equipements IKEA
#
class EquiptIKEA():
    def __init__(self,id_ikea):
        """ init eqt lampe IKEA """
        self.IdIkea=[int(l) for l in id_ikea]
        N = len(self.IdIkea)
        # init pont IKEA
        self.api     = api_factory(IP, KEY)
        self.gateway = Gateway()

        # recuperation info
        devices_command  = self.gateway.get_devices()
        devices_commands = self.api(devices_command)
        self.devices     = self.api(*devices_commands)

        # liste des lumieres
        lights = [dev for dev in self.devices if dev.has_light_control]
        # Print all lights
        if DEBUG:
            print("Liste des ampoules IKEA")
            for light in lights:
                print("\t",light.id,light.name,light.light_control.lights[0])
        # 
        self.LightIkea=[None]*N
        for k in range(N):
            Id = self.IdIkea[k]
            for light in lights:
                if light.id == Id :
                        self.LightIkea[k]=light.light_control.lights[0]
        self.reach =[None]*N
        self.state =[None]*N
        self.dimmer=[None]*N
        self.col   =[None]*N
        for k in range(N):
            light=self.LightIkea[k]
            self.reach[k] = light.device.reachable
            self.state[k] = light.state
            self.dimmer[k]= light.dimmer
            self.col[k]   = light.hex_color
        return
    
    def check_state(self,k):
        """ test si l'etat a change """
        change=False
        light=self.LightIkea[k]
        light.device.update()
        if light.device.reachable != self.reach[k] :
                self.reach[k] = light.device.reachable
                change=True
        if light.state != self.state[k] :
                self.state[k] = light.state
                change=True
        if light.dimmer != self.dimmer[k] :
                self.dimmer[k]= light.dimmer
                change =True
        return change

    def info(self):
        """ affiche etat """
        N = len(self.IdIkea)
        for k in range(N):
            light = self.LightIkea[k]
            light.device.update()
            if DEBUG: print(light.device.id,light.device.name,light.device.reachable,
                            light.state,light.dimmer,light.hex_color)
            if light.device.reachable:
                print("Eqt[%d] %s reach:%s,%s state=%s,%s dim=%d,%d col=%s "
                        %(light.device.id,light.device.name,light.device.reachable,self.reach[k],
                          light.state,self.state[k],light.dimmer,self.dimmer[k],light.hex_color))
            else :
                print("Eqt[%d] %s reach:%s,%s state=%s,%s"
                        %(light.device.id,light.device.name,light.device.reachable,self.reach[k],
                          light.state,self.state[k]))
        return

    def set_state(self,k,on=True):
        light=self.LightIkea[k]
        light.device.light_control.set_state(on)
        light.device.update()
        return

    def set_dimmer(self,k,dimmer=255):
        light=self.LightIkea[k]
        light.device.light_control.set_dimmer(dimmer)
        light.device.update()
        return

#
# test connection internet 
def internet(host="127.0.0.1", port=53, timeout=5): 
    """ Host:  OpenPort: 53/tcp Service: domain (DNS/TCP) """ 
    try: 
       socket.setdefaulttimeout(timeout) 
       socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port)) 
       return True 
    except Exception as ex: 
       print("Erreur connection internet:",ex)
       return False 
#
print("\tdaemon TRADFRI pour interface JEEDOM\n")
if (len(sys.argv)>1) and (sys.argv[1] == '-d') : DEBUG=True
#
# lecture configuration dans tradfri.cfg
#
conf = configparser.ConfigParser()
# repertoire courant ou dans /etc
conf.read(['tradfri.cfg','/etc/tradfri.cfg'])
# pont tradfri
IP     = conf.get('IKEA','IP')
KEY    = conf.get('IKEA','KEY')
IKEA_ID= conf.get('IKEA','IKEA_ID').split(sep=",")
if DEBUG: print("IKEA cfg:",IP,KEY,IKEA_ID)
# Jeedom
IP_JEEDOM  = conf.get('JEEDOM','IP_JEEDOM')
API_KEY    = conf.get('JEEDOM','API_KEY')
JEEDOM_ID  = conf.get('JEEDOM','JEEDOM_ID').split(sep=",")
if DEBUG: print("JEEDOM cfg:",IP_JEEDOM,API_KEY,JEEDOM_ID)

URL_JEEDOM = "http://"+IP_JEEDOM+"/core/api/jeeApi.php"

#
if DEBUG:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
else:
    # test connection externe 
    print("test connection internet :",IP_JEEDOM)
    while not internet(host=IP_JEEDOM, port=80):
      time.sleep(10)
    #
    time.sleep(10)
#

SESSION_JEEDOM = requests.Session()
# lecture des equipements lumieres JEEDOM
#
eqJEEDOM=EquiptJEEDOM(JEEDOM_ID)
# et equipement IKEA
eqIkea=EquiptIKEA(IKEA_ID)
N = len(eqIkea.LightIkea)
# init
for k in range(N):
    eqJEEDOM.set_state(k,eqIkea.state[k])
    eqJEEDOM.set_bright(k,eqIkea.dimmer[k])
    eqJEEDOM.set_reach(k,eqIkea.reach[k])
#
eqIkea.info()
eqJEEDOM.info()

print("\tBoucle sur %d Equipt\n\t================\n"%N)
sys.stdout.flush()
while True :
    eqIkea=EquiptIKEA(IKEA_ID)
    N = len(eqIkea.LightIkea)
    for k in range(N):
        if eqIkea.check_state(k):
            print("Changement etat equipement ",k)
            eqJEEDOM.set_state(k,eqIkea.state[k])
            eqJEEDOM.set_bright(k,eqIkea.dimmer[k])
            eqJEEDOM.set_reach(k,eqIkea.reach[k])
    if DEBUG:
        eqIkea.info()
        eqJEEDOM.info()
    delai=20
    if DEBUG:
        print("sleep ",delai)
    time.sleep(delai)
# fin
sys.exit(0)

