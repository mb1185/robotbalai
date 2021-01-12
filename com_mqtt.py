# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:18:19 2020

@author: mbaillot
"""

import paho.mqtt.client as mqtt

from flask import Flask, render_template, redirect, url_for, request 
from flask import jsonify
from flask_socketio import SocketIO

import json

app = Flask(__name__)
socketio = SocketIO(app)


labels = []
values = []

carte_sol_labels = ['test']
carte_sol_values = [{'x': 100, 'y': 100}]

parametres = []
parametres.append({"nom":"R_LIMIT_COURANT", "value": 30})
parametres.append({'nom':'R_DIAMETRE_ROUE', 'value': 60})
parametres.append({'nom':'R_DIAMTETRE_ENTRE_ROUE', 'value': 304})
parametres.append({'nom':'R_SEQ_DAV_TPS_RECULE', 'value': 500})
parametres.append({'nom':'R_SEQ_DAV_TPS_TOURNE', 'value': 1000})
parametres.append({'nom':'R_SEQ_DG_TPS_RECULE', 'value': 500})
parametres.append({'nom':'R_SEQ_DG_TPS_TOURNE', 'value': 1000})
parametres.append({'nom':'R_SEQ_DD_TPS_RECULE', 'value': 500})
parametres.append({'nom':'R_SEQ_DD_TPS_TOURNE', 'value': 1000})
parametres.append({'nom':'R_FACTEUR_DEF_VITESSE', 'value': 40})
parametres.append({'nom':'R_SEQ_TPS_STAB', 'value': 3000})


#fonction logger
def logger(data):
    socketio.emit("update_logger", data)   



def etat_mesure(data):
    print (data)
    #data = '{"I":0,"A":10,"D":55}'
    #data_json = json.loads(data.replace("'", "\""))
    data_json = json.loads(data)
    print ("rrr %s" % data_json)
    index = int(data_json['I'])
    angle = float(data_json['A'])
    mesure = float(data_json['D'])
    
    if index ==0:
        labels.clear()
        values.clear()
    
    if (mesure >= 1500.0):
        return
    

    labels.append(angle)
    values.append(mesure) 
    msg = {'labels':labels, 'values':values}
    socketio.emit("update_mesure360", msg)    

#mise a jour carte sol
def etat_carte_sol(data):
    data_json = json.loads(data)
    x = int(data_json['X'])
    y = int(data_json['Y'])
    carte_sol_values.append({'x': x, 'y': y})
    msg = {'labels':carte_sol_labels, 'values':carte_sol_values}
    socketio.emit("update_carte_sol", msg)
    

#mise a jour coordonnees
def etat_coordonnees(data):
    
    data_json = json.loads(data)
    x = float(data_json['X'])
    y = float(data_json['Y'])
    a = float(data_json['A']) 
    d = float(data_json['D']) 
    msg = {'X':x, 'Y':y , 'A':a , 'D':d}
    print (msg)
    socketio.emit("update_coordonnees", msg)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("robot_balai/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global labels, values
    print(msg.topic+" "+str(msg.payload))

    if (msg.topic == "robot_balai/debug"):
        logger(str(msg.payload.decode("utf-8")))
        
    if (msg.topic == "robot_balai/etat/mesure"):
        etat_mesure(str(msg.payload.decode("utf-8")))

    if (msg.topic == "robot_balai/etat/carte_sol"):
        etat_carte_sol(str(msg.payload.decode("utf-8")))

    if (msg.topic == "robot_balai/etat/coordonnees"):
        etat_coordonnees(str(msg.payload.decode("utf-8")))

        
    if (msg.topic == "robot_balai/etat/ina226"):
        data_json = json.loads(str(msg.payload.decode("utf-8")))
        socketio.emit("update_ina226", data_json)

    if (msg.topic == "robot_balai/etat/boussole"):
        data_json = json.loads(str(msg.payload.decode("utf-8")))
        socketio.emit("update_boussole", data_json)

    if (msg.topic == "robot_balai/etat/seq_auto"):
        data_json = json.loads(str(msg.payload.decode("utf-8")))
        socketio.emit("update_seq_auto", data_json)
        
    if (msg.topic == "robot_balai/etat/parametre"):
        data_json = json.loads(str(msg.payload.decode("utf-8")))
        socketio.emit("update_parametre", data_json)
        
    if (msg.topic == "robot_balai/etat/mesure360"):
        
        vstring = str(msg.payload.decode("utf-8"))
        ligne = vstring.split(";")
        index = int(ligne[0])
        angle = float(ligne[1])
        mesure =  float(ligne[2])
        
        if (index == 0 ):
            labels.clear()
            values.clear()
            
        if (index > 10 and angle == 0.0 ):
            msg = {'labels':labels, 'values':values}
            socketio.emit("update_mesure360", msg)
            return
        

        #labels.pop(index)
        labels.insert(index, angle)
        #values.pop(index)
        values.insert(index, mesure)  

        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.216", 1883, 60)
#client.connect("mqtt.eclipse.org", 1883)

client.loop_start()



for i in range (2):
    labels.append(str(i))
    values.append(str(i))
    

@app.route("/home")
def home():
    #client.publish("robot_balai/cmd/mesure360", "10;20;30")
    return render_template('index.html', title='Robot Balai', max=100, labels=labels, values=values)

@app.route("/parametres")
def vue_parametres():
    #client.publish("robot_balai/cmd/mesure360", "10;20;30")
    return render_template('parametres.html', title='Parametres', max=100, parametres = parametres)   


@socketio.on('effacer_carte_sol')   
def message_effacer_carte_sol(data):
    global carte_sol_labels, carte_sol_values
    carte_sol_labels = ['test']
    carte_sol_values = [{'x': 100, 'y': 100}]
    msg = {'labels':carte_sol_labels, 'values':carte_sol_values}
    socketio.emit("update_carte_sol", msg)
    

@socketio.on('cmd_mqtt')   
def message_cmd_mqtt(data):   
    print('topi:%s payload:%s' % (data['topic'],data['payload']))
    client.publish(data['topic'], data['payload'] )
    
    
if __name__ == '__main__':
    #app.run(host="localhost", port=8000, debug=True)
    socketio.run(app, port=8000, debug=True)
