# TRADFRI / JEEDOM

# Interface Jeedom avec le système TRADFRI IKEA pour la gestion des lumières

## Introduction
Pour pouvoir utiliser le système TRADFRI IKEA sous [JEEDOM](https://www.jeedom.com), le programme de domotique que j'utilise chez moi, j'ai développé les programmes python suivant pour la gestion des lumières avec JEEDOM.
Dans l'interface JEEDOM j'ai donc des widgets de la forme suivante,par exemple pour les lumières de l'escalier et de la salle TV, avec gestion de l'intensité et test de l'accès des lampes avec le pont (permet de savoir si l'interupteur est sur off)

![interface JEEDOM](https://github.com/mbuffat/Tradfri-JEEDOM/blob/master/tradfri.png)

## Installation
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
Le principe est d'avoir un daemon ("pytradfridaemon.py") qui met à jour l'état des ampoules dans les widgets sous Jeedom et un programme ("set_trafri.py") qui contrôle les ampoules (les allume ou les éteinds) depuis JEEDOM.

## "set_tradfri.py"  action sur le pont
Pour manipuler les ampoules, j'utilise le script set_trafri.py.

Avant de l'utiliser il faut le configurer en spécifiant l'adresse IP du pont et sa clé (écrite sous le boitier).

Sans argument, il donne la liste des equipements tradfri. 
Il permet d'avoir le numero (id) des ampoules installées.
```
set_tradfri.py
```
liste les equipements du pont
```
syntaxe: set_tradfri [on/off/dim] [val] ampoules_id

        Pont TRADFRI ip: 192.168.0.73

    devices 9
[<65541 - Variateur salle tv (TRADFRI wireless dimmer)>, <65539 - Détecteur Escalier bas (TRADFRI motion sensor)>, <65536 - Détecteur Escalier (TRADFRI motion sensor)>, <65538 - Ampoule Escalier 2 (TRADFRI bulb E27 opal 1000lm)>, <65544 - ampoule salle tv 2 (TRADFRI bulb GU10 WS 400lm)>, <65543 - Ampoule salle tv 1 (TRADFRI bulb GU10 WS 400lm)>, <65542 - Ampoule couloir bas (TRADFRI bulb E27 opal 1000lm)>, <65540 - Ampoule Escalier bas (TRADFRI bulb E27 opal 1000lm)>, <65537 - Ampoule Escalier 1 (TRADFRI bulb E14 WS opal 400lm)>]

    liste des ampoules 6
[<65538 - Ampoule Escalier 2 (TRADFRI bulb E27 opal 1000lm)>, <65544 - ampoule salle tv 2 (TRADFRI bulb GU10 WS 400lm)>, <65543 - Ampoule salle tv 1 (TRADFRI bulb GU10 WS 400lm)>, <65542 - Ampoule couloir bas (TRADFRI bulb E27 opal 1000lm)>, <65540 - Ampoule Escalier bas (TRADFRI bulb E27 opal 1000lm)>, <65537 - Ampoule Escalier 1 (TRADFRI bulb E14 WS opal 400lm)>] 
```

Pour allumer une liste d'ampoules de numero id1 id2 id2
```
set_trafri.py on id1 id2 ...
```
par exemple:
```
set_tradfri.py on 65543 65544 

Etat ampoule 65543
name  Ampoule salle tv 1
state  True
dimmmer  200
Etat ampoule 65544
name  ampoule salle tv 2
state  True
dimmmer  200
```
idem pour la commande off.

Pour la commande dim (gestion intensité) en passant en parametre la valeur de l'itensité de 0 à 255
```
set_tradfri.py dim 100 65543 65544 

Etat ampoule 65543
name  Ampoule salle tv 1
state  True
dimmmer  100
Etat ampoule 65544
name  ampoule salle tv 2
state  True
dimmmer  100
```

## daemon "tradfridaemon.py"

ce daemon tourne en permanence et met à jour les widgets sous JEEDOM (etat des lampes, intensité, joignable).
On peut le configurer en tant que service systemctl permettant sa gestion automatique.

Pour utiliser ce daemon, il faut le configurer en spécifiant l'adresse IP du pont et sa clé (écrite sous le boitier): variable IP et KEY , puis l'IP de JEEDOM et la clé API JEEDOM: variable IP_JEEDOM et API_KEY, ainsi que les widgets JEEDOM et les lumières tradfri associées: variable JEEDOM_ID et IKEA_ID.

Il faut donc d'abord créer autant de widget lumiere sous JEEDOM que de lampes IKEA. Chaque widget est associé à un virtuel avec les commandes suivantes:

- etat
- on 
- off
- bright
- setbright
- reach
- setreach

en suivant l'exemple suivant:
![widget JEEDOM](https://github.com/mbuffat/Tradfri-JEEDOM/blob/master/jeedom.png)

Avec les scénarios on associe les commandes on,off,setbright à la commande set_tradfri.py pour executer les commandes de contrôle sous JEEDOM.

## creation du service
pour installer le daemon en tant que service, on place le fichier tradfridaemon.service dans /etc/systemd/system
et le daemon tradfridaemon.py dans /usr/loca/sbin/

et on execute les commandes suivantes:
```
systemctl enable tradfridaemon
systemctl start tradfridaemon
```
