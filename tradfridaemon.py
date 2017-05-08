#! /usr/bin/env python3
# daemon tradfy 
import sys
import time
import socket
import pytradfri
import json
import requests
import pprint

# pont tradfri
IP="192.168.0.73"
KEY="lcxoHSTjJOxgZ6I4"
DEBUG=False
# Jeedom
#URL_JEEDOM = "http://192.168.0.16/core/api/jeeApi.php"
URL_JEEDOM = "http://127.0.0.1/core/api/jeeApi.php"
API_KEY    = "6tvyjdpb88jh1bdqli20"

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
    response = requests.post(URL_JEEDOM, data=json.dumps(PARAMS), headers=HEADERS)
    if response.status_code != 200 :
        print("Erreur API:",ID,methode," code:",response.status_code)
    return response
#
def JeedomCmd(ID,val=None):
    if val != None :
        DATA={"apikey" : API_KEY , "type" : 'cmd' , "id" : int(ID), "slider" : val}
    else:
        DATA={"apikey" : API_KEY , "type" : 'cmd' , "id" : int(ID), }
    response = requests.post(URL_JEEDOM, params=DATA)
    if response.status_code != 200 :
        print("CMD:",ID,val," code:",response.status_code)
    #print(response.url)
    return response
#
# equipements JEEDOM
# =================
class EquiptJEEDOM():
    """ gestion des widgets Lumieres Jeedom"""
    def __init__(self,lumid):
        JeedomAPI()
        self.LumId=lumid.copy()
        N=len(self.LumId)
        self.EtatId     = [None]*N
        self.SetOnId    = [None]*N
        self.SetOffId   = [None]*N
        self.BrightId   = [None]*N
        self.SetBrightId= [None]*N
        self.ReachId    = [None]*N
        self.SetReachId = [None]*N
        for k,lum in enumerate(self.LumId):
            rep = JeedomAPI(lum,"eqLogic::fullById").json()['result']['cmds']
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
            rep = JeedomAPI(self.EtatId[k],"cmd::execCmd").json()['result']
            self.etat[k]=int(rep['value'])
            rep = JeedomAPI(self.ReachId[k],"cmd::execCmd").json()['result']
            self.reach[k]=int(rep['value'])
            rep = JeedomAPI(self.BrightId[k],"cmd::execCmd").json()['result']
            self.bright[k]=int(rep['value'])
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
        else:
            rep = JeedomCmd(self.SetOffId[k])
        return
    def set_reach(self,k,state=True):
        if state :
            rep = JeedomCmd(self.SetReachId[k],100)
        else :
            rep = JeedomCmd(self.SetReachId[k],0)
            rep = JeedomCmd(self.SetOffId[k])
        return
    def set_bright(self,k,level=0):
        rep = JeedomCmd(self.SetBrightId[k],level)
        self.bright[k]=level
        return
#
# equipements IKEA
#
class EquiptIKEA():
    def __init__(self,id_ikea):
        """ init eqt lampe IKEA """
        self.IdIkea=id_ikea.copy()
        N = len(self.IdIkea)
        # init pont
        api = pytradfri.coap_cli.api_factory(IP, KEY)
        gateway = pytradfri.gateway.Gateway(api)
        # liste des lumieres
        devices = gateway.get_devices()
        lights = [dev for dev in devices if dev.has_light_control]
        # Print all lights
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
            print("Eqt[%d] %s reach:%s,%s state=%s,%s dim=%d,%d col=%s "
                        %(light.device.id,light.device.name,light.device.reachable,self.reach[k],
                          light.state,self.state[k],light.dimmer,self.dimmer[k],light.hex_color))
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
# test connection externe (LMS)
while not internet(host="192.168.0.11", port=9090):
      time.sleep(10)
#
# lecture des equipements lumieres JEEDOM
#
eqJEEDOM=EquiptJEEDOM(["617","681","680"])

# et equipement IKEA
eqIkea=EquiptIKEA([65538,65544,65540])
N = len(eqIkea.LightIkea)
# init
for k in range(N):
    eqJEEDOM.set_state(k,eqIkea.state[k])
    eqJEEDOM.set_bright(k,eqIkea.dimmer[k])
    eqJEEDOM.set_reach(k,eqIkea.reach[k])
#
eqIkea.info()
eqJEEDOM.info()

print("Boucle sur %d Equipt "%(N))
sys.stdout.flush()
while True :
    for k in range(N):
        if eqIkea.check_state(k):
            print("Changement etat equipement ",k)
            eqJEEDOM.set_state(k,eqIkea.state[k])
            eqJEEDOM.set_bright(k,eqIkea.dimmer[k])
            eqJEEDOM.set_reach(k,eqIkea.reach[k])
            if DEBUG:
                eqIkea.info()
                eqJEEDOM.info()
    time.sleep(5)
# fin
sys.exit(0)

