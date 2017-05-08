# TRADFRI / JEEDOM

# Interface Jeedom avec le système TRADFRI IKEA pour la gestion des lumières

## Introduction
Pour pouvoir utiliser le système TRADFRI IKEA sous [JEEDOM](https://www.jeedom.com), le programme de domotique que j'utilise chez moi, j'ai développé les programmes python suivant pour la gestion des lumières avec JEEDOM.
Dans l'interface JEEDOM j'ai donc des widgets de la forme suivante

![interface JEEDOM]()

##Installation
Il faut installer la bibliothèque python3 pytradfri (instructions tirées de [https://github.com/ggravlingen/pytradfri](https://github.com/ggravlingen/pytradfri)).

 Il faut pour cela d'abord installer libcoap, (sous root) 
```
$ apt-get install libtool
$ git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
$ cd libcoap
$ ./autogen.sh
$ ./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
$ make
$ make install
```

Il faut éventuellement installer des packages manquants (pour moi ctags)
puis installer ensuite la librairie pytradfri avec pip3 (version python3) 

```
pip3 install pytradfri
```

## action sur le pont
pour manipuler les ampoules, j'utilise le script set_trafri.py 

sans argument, la commande 
'''
set_tradfri.py
'''
liste les equipements du pont
'''
syntaxe: set_tradfri [on/off/dim] [val] ampoules_id

        Pont TRADFRI ip: 192.168.0.73

    devices 9
[<65541 - Variateur salle tv (TRADFRI wireless dimmer)>, <65539 - Détecteur Escalier bas (TRADFRI motion sensor)>, <65536 - Détecteur Escalier (TRADFRI motion sensor)>, <65538 - Ampoule Escalier 2 (TRADFRI bulb E27 opal 1000lm)>, <65544 - ampoule salle tv 2 (TRADFRI bulb GU10 WS 400lm)>, <65543 - Ampoule salle tv 1 (TRADFRI bulb GU10 WS 400lm)>, <65542 - Ampoule couloir bas (TRADFRI bulb E27 opal 1000lm)>, <65540 - Ampoule Escalier bas (TRADFRI bulb E27 opal 1000lm)>, <65537 - Ampoule Escalier 1 (TRADFRI bulb E14 WS opal 400lm)>]

    liste des ampoules 6
[<65538 - Ampoule Escalier 2 (TRADFRI bulb E27 opal 1000lm)>, <65544 - ampoule salle tv 2 (TRADFRI bulb GU10 WS 400lm)>, <65543 - Ampoule salle tv 1 (TRADFRI bulb GU10 WS 400lm)>, <65542 - Ampoule couloir bas (TRADFRI bulb E27 opal 1000lm)>, <65540 - Ampoule Escalier bas (TRADFRI bulb E27 opal 1000lm)>, <65537 - Ampoule Escalier 1 (TRADFRI bulb E14 WS opal 400lm)>] 
'''
