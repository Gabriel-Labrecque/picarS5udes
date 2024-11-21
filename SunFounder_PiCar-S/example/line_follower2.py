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
from picar import front_wheels
from picar import back_wheels
import time
import picar

picar.setup()

#REFERENCES = [61.0, 67.5, 42.0, 85.5, 83.0] #plancher
#REFERENCES = [37.5, 38.5, 33.5, 43.5, 37.0] #TABLE GRISE
#REFERENCES = [28.0, 28.0, 24.0, 32.5, 27.5]#TABLE ORANGE
REFERENCES = [29.5, 29.5, 24.5, 35.5, 29.5]#sac plastique blanc

#calibrate = True
calibrate = False
forward_speed = 80
backward_speed = 70
turning_angle = 40

max_off_track_count = 40

delay = 0.0005

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
lf = Line_Follower.Line_Follower()
isturnLeft = False
isturnRight = False
lf.references = REFERENCES
fw.ready()
bw.ready()
fw.turning_max = 45
compteurTurnAvance1 = 500
compteurTurnRecule = 300
compteurTurnAvance2 = 60
lastSpeed = 60
lastSens = "forward"
targetSens = "forward"
isCompteurTurnRecule = False
def straight_run():
    print("straight_run")
    while True:
        bw.speed = 60
        bw.forward()
        fw.turn_straight()


def setup():
    if calibrate:
        cali()

def main():
    global turning_angle
    global isturnRight
    global isturnLeft
    global compteurTurnAvance1
    global isCompteurTurnRecule
    global compteurTurnRecule 
    global compteurTurnAvance2
    global lastSpeed
    global lastSens
    global targetSens
    print("1")
    ResetcompteurTurnAvance1 = 500
    ResetcompteurTurnRecule = 300
    ResetcompteurTurnAvance2 = 60
    off_track_count = 0
    bw.speed = forward_speed
    a_step = 3
    b_step = 10
    c_step = 30
    d_step = 50
    bw.forward()


    while True:


        lt_status_now = lf.read_digital()

        if lt_status_now == [0,0,1,0,0] and not isCompteurTurnRecule:
            print("straight")
            speed = adjust_speed(60, lastSpeed=lastSpeed , increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
            print(speed)
            bw.speed = speed
            bw.forward()
            step = 0
            compteurTurnAvance1 = ResetcompteurTurnAvance1
            compteurTurnRecule = ResetcompteurTurnRecule
            compteurTurnAvance2 = ResetcompteurTurnAvance2
            isturnLeft = False
            isturnRight = False
        elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0] and not isturnLeft and not isturnRight :
            print("left")
            step = a_step
            speed = adjust_speed(60, lastSpeed=lastSpeed , increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
            print(speed)
            bw.speed = speed
        elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]and not isturnLeft and not isturnRight:
            step = b_step
            print("right")
            speed = adjust_speed(40, lastSpeed=lastSpeed , increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
            print(speed)
            bw.speed = speed
        elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]and not isturnLeft and not isturnRight:
            step = c_step
            speed = adjust_speed(30, lastSpeed=lastSpeed , increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
            print(speed)
            bw.speed = speed
        elif lt_status_now == [1,0,0,0,0] and not isturnRight and not isturnLeft :
            step = d_step
            isturnLeft = True
        elif lt_status_now == [0,0,0,0,1] and not isturnRight and not isturnLeft:
            step = d_step
            isturnRight = True
     
            
        if lt_status_now == [0,0,1,0,0] and not isCompteurTurnRecule:
            off_track_count = 0
            fw.turn(90)

        elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0]) and not isturnRight and not isturnLeft:
            off_track_count = 0
            turning_angle = int(90 - step)
            
  
        elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1]) and not isturnRight and not isturnLeft:
            off_track_count = 0
            turning_angle = int(90 + step)
            
        if isturnLeft and not isturnRight:
            if compteurTurnAvance1 > 0:
                turning_angle = int(90 - c_step)
                fw.turn(turning_angle) 
                speed = adjust_speed(25, lastSpeed=lastSpeed , increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
                bw.speed = speed
                bw.forward()
                compteurTurnAvance1 -= 1
                isCompteurTurnRecule = False
                lastSens="forward"
            elif compteurTurnRecule > 0 and compteurTurnAvance1 == 0:
                turning_angle = int(90 - d_step)
                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="backward", lastSens=lastSens)
                bw.speed = speed
                fw.turn(turning_angle)
                bw.backward()
                compteurTurnRecule -= 1
                isCompteurTurnRecule = False
                lastSens="backward"
            elif compteurTurnAvance2 > 0 and compteurTurnRecule == 0:
                turning_angle = int(90 - d_step)
                fw.turn(turning_angle)
                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
                bw.speed = speed
                bw.forward()
                compteurTurnAvance2 -= 1
                isCompteurTurnRecule = False
                lastSens="forward"
            elif compteurTurnAvance2 == 0:   
                bw.stop()
                compteurTurnAvance1 = ResetcompteurTurnAvance1
                compteurTurnRecule = ResetcompteurTurnRecule
                compteurTurnAvance2 = ResetcompteurTurnAvance2
                isCompteurTurnRecule = False
                lastSens="forward"
            else:
                bw.stop()
            time.sleep(delay) 
            lastSpeed = bw.speed
            off_track_count = 0                
                
            
        elif isturnRight and not isturnLeft:
           
 
            print("isturnRight")
            if compteurTurnAvance1 > 0:
                isCompteurTurnRecule = False
                print("compteurTurnAvance1")
                print(compteurTurnAvance1)
                turning_angle = int(90 + c_step)
                fw.turn(turning_angle)
                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
                bw.speed = speed
                bw.forward()
                compteurTurnAvance1 -= 1
                lastSens="forward"
            elif compteurTurnRecule > 0 and compteurTurnAvance1 == 0 :
                isCompteurTurnRecule = False
                turning_angle = int(90 - d_step)
                print("compteurTurnRecule")
                print(compteurTurnRecule)

                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="backward", lastSens=lastSens)
                bw.speed = speed
                fw.turn(turning_angle)
                bw.backward()
                compteurTurnRecule -= 1
                lastSens="backward"
            elif compteurTurnAvance2 > 0 and compteurTurnRecule == 0:

                print("compteurTurnAvance2")
                print(compteurTurnAvance2)
                turning_angle = int(90 + d_step)
                fw.turn(turning_angle)
                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
                bw.speed = speed
                bw.forward()
                compteurTurnAvance2 -= 1
                isCompteurTurnRecule = False
                lastSens="forward"
            elif compteurTurnAvance2 == 0:
                print("fin")
                print(compteurTurnAvance2)
                speed = adjust_speed(25, lastSpeed=lastSpeed, increment=5, delay=delay, targetSens="forward", lastSens=lastSens)
                bw.speed = speed
                time.sleep(0.5) 
                compteurTurnAvance1 = ResetcompteurTurnAvance1
                compteurTurnRecule = ResetcompteurTurnRecule
                compteurTurnAvance2 = ResetcompteurTurnAvance2
                isCompteurTurnRecule = False
                lastSens="forward"
            else:
                bw.stop() 
            time.sleep(delay)
            off_track_count = 0
            lastSpeed = bw.speed  
            lastSens ="forward"

        
       

           
        else:
            off_track_count = 0
        if not isturnRight and not isturnLeft:  
            fw.turn(turning_angle)
            time.sleep(delay) 
            lastSpeed = bw.speed
""" 

        elif lt_status_now == [0,0,0,0,0] and not isturnRight and not isturnLeft:
            off_track_count += 1
            if off_track_count > max_off_track_count:
                #tmp_angle = -(turning_angle - 90) + 90
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
                time.sleep(0.2)"""





def adjust_speed(target_speed = 60, lastSpeed = 60, increment=5, delay=0.0005, targetSens="forward", lastSens="forward"):
    # Si la direction cible est différente de la direction précédente, on ralentit d'abord à zéro
    print("2")
    if targetSens != lastSens:
        while lastSpeed > 0:
            print("while lastSpeed > 0")
            lastSpeed = max(lastSpeed - increment, 0)  # Ralentir progressivement
            bw.speed = lastSpeed
            # Maintenir la direction actuelle avant le changement
            if lastSens == "forward":
                bw.forward()
            else:
                bw.backward()
            time.sleep(delay)
        # La vitesse est maintenant à zéro; on peut changer de sens
        lastSpeed = 0  # Réinitialiser la vitesse à zéro pour le changement de direction
    
    # Maintenant, ajuster la vitesse pour atteindre `target_speed` dans la nouvelle direction
    while lastSpeed != target_speed:
        print("3")
        if lastSpeed < target_speed:
            lastSpeed = min(lastSpeed + increment, target_speed)
        elif lastSpeed > target_speed:
            lastSpeed = max(lastSpeed - increment, target_speed)
        
        bw.speed = lastSpeed
        print("4")
        # Appliquer la nouvelle direction
        if targetSens == "forward":
            bw.forward()
        elif targetSens == "backward":
            bw.backward()
        
        time.sleep(delay)
    return lastSpeed



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
                main()
                straight_run()
        except Exception as e:
            print(e)
            print('error try again in 5')
            destroy()
            time.sleep(5)
    except KeyboardInterrupt:
        destroy()

