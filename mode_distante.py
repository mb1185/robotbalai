# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:18:19 2020

@author: mbaillot
Gestion du mode distant robobalai
"""

import threading, time
import json

class gestion_distant (threading.Thread):
    def __init__ (self, clientmqtt):
        threading.Thread.__init__ (self)
        self.activation = False
        self.cmd_ec = False
        self.num_commande = 0
        self.status = {"N": 0, "E1": 0, "E2" :0, "E3": 0, "E4": 0, "E5": 0}
        self.terminated = False #Permet de stopper le thread
        print ("Instance gestion distant")
        self._clientmqtt = clientmqtt



    def run(self):
        while (not self.terminated):
            time.sleep(2)
            if self.activation:
                if not self.cmd_ec:
                    self.calcul_cmd()
            else:
                self.cmd_ec = False
                self.num_commande = 0

    def terminate(self):
        self.terminated = True


    def calcul_cmd(self):
        print ("Gestion distance: calcul commande")
        self.cmd_ec = True
        self.num_commande += 1
        topic = "robot_balai/cmd_mcrd"
        payload = {'N': self.num_commande, 'P1' : 1, 'P2' : 2, 'P3' : 3, 'P4' : 4}
        self._clientmqtt.publish(topic, json.dumps(payload))
        #Envoi commande
        

    def set_status(self, datajson):
        self.status_num_commande = int(datajson["N"])
        self.status_etat_commande = int(datajson["E1"])
        self.status_defaut_arret = int(datajson["E2"])
        self.status_x = int(datajson["E3"])
        self.status_y = int(datajson["E4"])
        self.status_a = int(datajson["E5"])

        print("Set Status:", datajson)
        print ("Status Distant  Num cmd: ", self.status_num_commande)
        print ("Status Distant Etat cmd: ", self.status_etat_commande)
        print ("Status Distant Defaut arret: ", self.status_defaut_arret)
        print ("Status Distant: X ", self.status_x)
        print ("Status Distant: Y", self.status_y)
        print ("Status Distant: A", self.status_a)
        print ("Distant: Num cmd ", self.num_commande)

        #Commande terminé
        if self.status_num_commande == self.num_commande:
            if self.status_etat_commande == 2: #Commande terminée
                self.cmd_ec = False

    
    
