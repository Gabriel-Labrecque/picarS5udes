#!/usr/bin/env python
'''
**********************************************************************
* Filename    : line_follower
* Description : An example for sensor car kit to followe line
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-21    New release
**********************************************************************
'''

from SunFounder_Line_Follower import Line_Follower
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from picar import front_wheels
from picar import back_wheels
import time
import picar
import random
import math
import threading
import csv

picar.setup()

#REFERENCES = [61.0, 67.5, 42.0, 85.5, 83.0] #plancher
#REFERENCES = [37.5, 38.5, 33.5, 43.5, 37.0] #TABLE GRISE
REFERENCES = [28.0, 28.0, 24.0, 32.5, 27.5]#TABLE ORANGE
#REFERENCES = [29.5, 29.5, 24.5, 35.5, 29.5]#sac plastique blanc
#REFERENCES =  [45.5, 45.0, 41.5, 51.5, 46.5]
#REFERENCES = [38.5, 40.5, 35.5, 50.0, 42.0]


# Capteur Ultrason
ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
back_distance = 10
turn_distance = 20
force_turning = 0    # 0 = random direction, 1 = force left, 2 = force right, 3 = orderdly
last_angle = 90
cptCompTourneStep1 = 100
cptCompTourneStep2 = 200
cptCompTourneStep3 = 200
cptCompTourneStep4 =200
cptCompTourneStep5 =200
isObstacle = False
thread_capteurDistance =0
distance =0

#calibrate = True
calibrate = False
isTurnExtremeLeft = False
isTurnExtremeRight = False
isReturn = False
forward_speed = 80
backward_speed = 70
turning_angle = 40
cptStraightAfterExtremeTurn = 60
cptTurnExtremeStep1 = 400
cptTurnExtremeStep2= 250
cptTurnExtremeStep3 = 100
cptReturn = 100
lastSpeedSens = (30, "forward") 

max_off_track_count = 40

delay = 0.0005

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
lf = Line_Follower.Line_Follower()

lf.references = REFERENCES
fw.ready()
bw.ready()
fw.turning_max = 45


targetSens = "forward"
def straight_run():
    while True:
        
        bw.speedLeft = 70
        bw.speedRight = 30
        bw.forwardLeft()
        #bw.forward()
        #fw.turn_straight()

def getDistance():
    global distance
    global isObstacle
    alpha  = 0.4
    prevDistance = 0
    nom_fichier = 'donnees_30cm.csv'
    compteurObstacle =0
    while ( not isObstacle):
        distance = ua.get_distance()
        #distance = math.ceil((ua.get_distance() * alpha)+((1-alpha) * prevDistance))
        prevDistance = distance
        """ compteurObstacle +=1
        if(compteurObstacle>20):
            if (distance <11):
                isObstacle = True
                bw.stop() """
        with open(nom_fichier, mode='a', newline='', encoding='utf-8') as fichier:  # Mode 'a' pour ajouter les données
                writer = csv.writer(fichier)
                
                # Écrire la distance sous la colonne "Donner a 10cm"
                writer.writerow([distance])  # Ajouter la distance à une nouvelle ligne       
        print("distance: %scm" % distance)
        time.sleep(0.2)

    
       

def setup():
    if calibrate:
        cali()

def main():
    global turning_angle
    global isTurnExtremeRight
    global isTurnExtremeLeft
    global isReturn 
    global cptTurnExtremeStep1
    global cptTurnExtremeStep2
    global cptTurnExtremeStep3
    global cptCompTourneStep1
    global cptCompTourneStep2
    global cptCompTourneStep3
    global cptCompTourneStep4
    global cptCompTourneStep5
    global cptStraightAfterExtremeTurn
    global cptReturn
    global lastSpeedSens
    global targetSens
    global isObstacle

    global distance
    global thread_capteurDistance
    thread_capteurDistance = threading.Thread(target=getDistance)

    off_track_count = 0
    bw.speed = lastSpeedSens[0]
    a_step = 3
    b_step = 10
    c_step = 30
    d_step = 45
    strong_speed = 50
    middle_speed  = 45
    small_speed = 40
    very_small_speed = 35
    mini_speed = 30
    isObstacle = False
    bw.stop()
    thread_capteurDistance.start()
    time.sleep(1)
    while (True):
        lt_status_now = lf.read_digital()
        time.sleep(10000)
    while True:
        lt_status_now = lf.read_digital()
        """ if distance < :
            #lastSpeedSens = adjust_speed_and_sens(target_speed=0, lastSpeed=lastSpeedSens[0], increment=4, targetSens="forward", lastSens=lastSpeedSens[1])
            bw.stop()
            #isObstacle = True """
            
        if (isObstacle):
            
            print("isObstacle")
            time.sleep(0.2)
            thread_capteurDistance.join()
            #obstacle()
        #### AJUSTE VITESSE #######
        else:
            if lt_status_now == [0,0,1,0,0]:
                if isTurnExtremeLeft or isTurnExtremeRight:
                    bw.stop()
                    lastSpeedSens = (1, "forward") 
                    cptStraightAfterExtremeTurn = 100
                    fw.turn(90)
                    time.sleep(0.2)
                    isTurnExtremeLeft = False
                    isTurnExtremeRight = False
                if cptStraightAfterExtremeTurn > 0:
                    target_speed=mini_speed
                    #print(target_speed)
                    cptStraightAfterExtremeTurn -= 1
                else: 
                    target_speed=strong_speed
                    cptStraightAfterExtremeTurn = 60
                step = 0
                """ if target_speed==mini_speed:
                    print(target_speed) """
                lastSpeedSens = adjust_speed_and_sens(target_speed=target_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3 = reset_compteur(cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3)

            
            elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0] and isNotTurnExtreme() :
                step = a_step
                lastSpeedSens = adjust_speed_and_sens(target_speed=middle_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                
                
            elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0] and isNotTurnExtreme():
                step = b_step
                lastSpeedSens = adjust_speed_and_sens(target_speed=small_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                
                
            elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1] and isNotTurnExtreme():
                step = c_step
                lastSpeedSens = adjust_speed_and_sens(target_speed=very_small_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
          
          #### AJUSTE ANGLE #######             
            if lt_status_now == [0,0,1,0,0]:
                off_track_count = 0
                fw.turn(90)

            elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0]) and isNotTurnExtreme():
                off_track_count = 0
                turning_angle = int(90 - step)
                
      
            elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1]) and isNotTurnExtreme():
                off_track_count = 0
                turning_angle = int(90 + step)
                
          #### AJUSTE CAS TURN EXTREME #######            
                
                
            elif lt_status_now == [1,0,0,0,0] and isNotTurnExtreme():
                off_track_count = 0
                isTurnExtremeLeft = True
                
            elif lt_status_now == [0,0,0,0,1] and isNotTurnExtreme():
                off_track_count = 0
                isTurnExtremeRight = True
         

                    
           #### EXECUTE CAS TURN EXTREME #######     
                    
                
            elif isTurnExtremeLeft and not isTurnExtremeRight:
                if cptTurnExtremeStep1 == 500 :
                        print("isTurnExtremeLeft    onAvance")
                if cptTurnExtremeStep1 > 0:
                    turning_angle = int(90 - c_step)
                    fw.turn(turning_angle)  # Angle ajusté pour avancer
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
                    
                   
                    cptTurnExtremeStep1 -= 1
                 
                elif cptTurnExtremeStep2> 0 and cptTurnExtremeStep1 == 0:
                    if cptTurnExtremeStep2== 350 :
                        print("isTurnExtremeLeft   onRecule")
                    tmp_angle = -(d_step - 90) + 90
                    tmp_angle *= fw.turning_max
                    fw.turn(tmp_angle)
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=12, targetSens="backward", lastSens=lastSpeedSens[1])
                    cptTurnExtremeStep2-= 1
                  
                elif cptTurnExtremeStep3 > 0 and cptTurnExtremeStep2== 0:
                    if cptTurnExtremeStep3 == 60:
                        print("isTurnExtremeLeft   onAvanceApresRecule")
                    turning_angle = int(90 - b_step)
                    fw.turn(turning_angle)
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                    cptTurnExtremeStep3 -= 1
                 
                elif cptTurnExtremeStep3 == 0:   
                    print("fin")
                    cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3 = reset_compteur(cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3)

                 
                               
                    
                
            elif isTurnExtremeRight and not isTurnExtremeLeft:
               
                if cptTurnExtremeStep1 == 500 :
                        print("isTurnExtremeRight    onAvance")
                if cptTurnExtremeStep1 > 0:
               
                    turning_angle = int(90 + c_step)
                    fw.turn(turning_angle)
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
                    
                    
                    cptTurnExtremeStep1 -= 1
                    
                elif cptTurnExtremeStep2> 0 and cptTurnExtremeStep1 == 0 :
                    if cptTurnExtremeStep2== 350 :
                        print("isTurnExtremeRight   onRecule")
                  
                    turning_angle = int(90 - d_step)
                    tmp_angle = (d_step-90)/abs(90-d_step)
                    tmp_angle *= fw.turning_max
                    fw.turn(tmp_angle)
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=10, targetSens="backward", lastSens=lastSpeedSens[1])
                    cptTurnExtremeStep2-= 1
                    
                elif cptTurnExtremeStep3 > 0 and cptTurnExtremeStep2== 0:
                    if cptTurnExtremeStep3 == 60:
                        print("isTurnExtremeRight   onAvanceApresRecule")
                    turning_angle = int(90 + b_step)
            
                    fw.turn(turning_angle)
                    lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                    
                    bw.forward()
                    cptTurnExtremeStep3 -= 1
                 
                elif cptTurnExtremeStep3 == 0:
                    cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3 = reset_compteur(cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3)
     
               



            else:
                off_track_count = 0
                
            if isNotTurnExtreme():  
                fw.turn(turning_angle)
                time.sleep(delay)           
        prevDistance = distance
        '''if lt_status_now == [0,0,0,0,0] and not isTurnExtremeRight and not isTurnExtremeLeft:
            off_track_count += 1
            if off_track_count > max_off_track_count:#tmp_angle = -(turning_angle - 90) + 90
                tmp_angle = (turning_angle-90)/abs(90-turning_angle)
                tmp_angle *= fw.turning_max
                bw.speed = backward_speed
                bw.backward()
                fw.turn(tmp_angle)
                
                lf.wait_tile_center()
                bw.stop()

                fw.turn(turning_angle)
                time.sleep(0.2)
                bw.speed = forward_speed
                bw.forward()
                time.sleep(0.2)
          '''  
       
def reset_compteur(cptTurnExtremeStep1 = 0, cptTurnExtremeStep2= 0, cptTurnExtremeStep3 = 0):
    cptTurnExtremeStep1 = 400
    cptTurnExtremeStep2 = 250
    cptTurnExtremeStep3 = 60

    return cptTurnExtremeStep1, cptTurnExtremeStep2, cptTurnExtremeStep3
def reset_compteur_obstacle(cptCompTourneStep1 = 0, cptCompTourneStep2= 0, cptCompTourneStep3 = 0, cptCompTourneStep4 = 0, cptCompTourneStep5= 0):
    cptCompTourneStep1 = 100
    cptCompTourneStep2 = 200
    cptCompTourneStep3 = 200
    cptCompTourneStep4 =200
    cptCompTourneStep5 =200
    return cptCompTourneStep1, cptCompTourneStep2, cptCompTourneStep3, cptCompTourneStep4, cptCompTourneStep5
def isNotTurnExtreme():
    return (not isTurnExtremeRight and not isTurnExtremeLeft)

def adjust_speed_and_sens(target_speed=60, lastSpeed=60, increment=10, targetSens="forward", lastSens="forward"):
    # Étape 1 : Si les directions sont différentes, ralentir jusqu'à zéro
    if targetSens != lastSens:
        if lastSpeed > 0:
            lastSpeed = max(lastSpeed - increment, 0)  # Réduire la vitesse progressivement
            print(lastSpeed)
        elif lastSpeed <= 0:
            lastSpeed = 0
            lastSens = targetSens  # Mettre à jour la direction une fois la vitesse à zéro
            bw.stop()
            time.sleep(0.2)
    # Étape 2 : Si la direction est correcte, ajuster la vitesse pour atteindre la cible
    elif lastSpeed != target_speed and targetSens == lastSens:
        
        if lastSpeed < target_speed:
            
            lastSpeed = min(lastSpeed + increment, target_speed)
           
        elif lastSpeed > target_speed:
            lastSpeed = max(lastSpeed - increment, target_speed)
           
    bw.speed = lastSpeed  
    if lastSens == "forward":
        bw.forward()
    if lastSens == "backward":
        bw.backward()
    return lastSpeed, lastSens

def rand_dir():
    global last_angle, last_dir
    if force_turning == 0:
        _dir = random.randint(0, 1)
    elif force_turning == 3:
        _dir = not last_dir
        last_dir = _dir
        print('last dir  %s' % last_dir)
    else:
        _dir = force_turning - 1
    angle = (90 - fw.turning_max) + (_dir * 2* fw.turning_max)
    last_angle = angle
    return angle
    
def start_avoidance():
    global last_angle
    print('start_avoidance')
    very_small_speed = 35
    prevDistance = 0
    alpha  = 0.2
    count = 0
    while True:
        distance = math.ceil((ua.get_distance() + 5)* alpha+(1-alpha) * prevDistance)
        
        print("distance: %scm" % distance)
        if distance > 30   :
            adjust_speed_and_sens(target_speed=very_small_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="backward", lastSens=lastSpeedSens[1])
        elif  distance <11 :
            count = 0
            if distance < back_distance: # backward
                print( "backward")
                fw.turn(opposite_angle())
                bw.backward()
                bw.speed = backward_speed
                fw.turn(opposite_angle())
                bw.forward()
            elif distance < turn_distance: # turn
                print("turn")
                fw.turn(rand_dir())
                bw.forward()
                bw.speed = forward_speed
            else:
                fw.turn_straight()
                bw.forward()
                bw.speed = forward_speed

        else:                        # forward
            fw.turn_straight()
            """ if count > timeout:  # timeout, stop;
                bw.stop()
            else:
                bw.backward()
                bw.speed = forward_speed
                count += 1 """
        prevDistance = distance
        
def obstacle():
    global cptCompTourneStep1
    global cptCompTourneStep2
    global cptCompTourneStep3
    global cptCompTourneStep4
    global cptCompTourneStep5
    global lastSpeedSens
    global targetSens
    global isObstacle
    a_step = 3
    b_step = 10
    c_step = 30
    d_step = 45
    strong_speed = 50
    middle_speed  = 45
    small_speed = 40
    very_small_speed = 35
    mini_speed = 30

    if cptCompTourneStep1 > 0:
        fw.turn(90)
        bw.backward()
        lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=5, targetSens="backward", lastSens=lastSpeedSens[1])
        cptCompTourneStep1 -= 1
    elif cptCompTourneStep2> 0 and cptCompTourneStep1 == 0 :
        turning_angle = int(90 - d_step)
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneStep2-= 1
        
    elif cptCompTourneStep3 > 0 and cptCompTourneStep2== 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneStep3 -= 1
    elif cptCompTourneStep4> 0 and cptCompTourneStep3 == 0 :
        turning_angle = int(90 + d_step)
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneStep4-= 1
        
    elif cptCompTourneStep5 > 0 and cptCompTourneStep4== 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=mini_speed, lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneStep5 -= 1 
    elif cptCompTourneStep5 == 0:
        cptCompTourneStep1, cptCompTourneStep2, cptCompTourneStep3 , cptCompTourneStep4, cptCompTourneStep5 = reset_compteur_obstacle(cptCompTourneStep1, cptCompTourneStep2, cptCompTourneStep3 , cptCompTourneStep4, cptCompTourneStep5)
def stop():
    bw.stop()
    fw.turn_straight()

def opposite_angle():
    global last_angle
    if last_angle < 90:
        angle = last_angle + 2* fw.turning_max
    else:
        angle = last_angle - 2* fw.turning_max
    last_angle = angle
    return angle
  
def cali():
    references = [0, 0, 0, 0, 0]
    print("go")
    time.sleep(10)
    print("cali for module:\n  first put all sensors on white, then put all sensors on black")
    mount = 100
    fw.turn(70)
    print("\n cali white")
    time.sleep(4)
    fw.turn(90)
    white_references = lf.get_average(mount)
    fw.turn(95)
    time.sleep(0.5)
    fw.turn(85)
    time.sleep(0.5)
    fw.turn(90)
    time.sleep(1)

    fw.turn(110)
    print("\n cali black")
    time.sleep(4)
    fw.turn(90)
    black_references = lf.get_average(mount)
    fw.turn(95)
    time.sleep(0.5)
    fw.turn(85)
    time.sleep(0.5)
    fw.turn(90)
    time.sleep(1)

    for i in range(0, 5):
        references[i] = (white_references[i] + black_references[i]) / 2
    lf.references = references
    print("Middle references =", references)
    time.sleep(1)

def destroy():
    bw.stop()
    fw.turn(90)

if __name__ == '__main__':
    try:
        try:
            while True:
                setup()
                #start_avoidance()
                #bw.forwardLeft()
                main()
                #straight_run()
        except Exception as e:
            print(e)
            print('error try again in 5')
            destroy()
            time.sleep(5)
    except KeyboardInterrupt:
        destroy()


