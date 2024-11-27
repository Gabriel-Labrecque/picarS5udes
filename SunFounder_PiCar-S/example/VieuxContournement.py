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
import threading
import math

picar.setup()

#REFERENCES = [61.0, 67.5, 42.0, 85.5, 83.0] #plancher
#REFERENCES = [37.5, 38.5, 33.5, 43.5, 37.0] #TABLE GRISE
#REFERENCES = [28.0, 28.0, 24.0, 32.5, 27.5]#TABLE ORANGE
#REFERENCES = [29.5, 29.5, 24.5, 35.5, 29.5]#sac plastique blanc
#REFERENCES = [45.5, 45.0, 41.5, 51.5, 46.5]
REFERENCES = [42.5, 43.0, 37.5, 48.0, 41.0]



# Capteur Ultrason
ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
back_distance = 10
turn_distance = 20
force_turning = 0    # 0 = random direction, 1 = force left, 2 = force right, 3 = orderdly
last_angle = 90
cptCompTourneSteps = [100, 200, 200, 200, 200]

isObstacle = False






#calibrate = True
calibrate = False
isTurnExtremeLeft, isTurnExtremeRight = False, False
forward_speed = 80
backward_speed = 70
turning_angle = 40
cptStraightAfterExtremeTurn = 60
cptTurnExtremeSteps = [400, 250, 100]
angleLevel = [0, 3, 10, 30, 45]
speedLevel = [50, 45, 40, 35, 30]
lastSpeedSens = (1, "forward") 

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
        bw.speed = 60
        bw.forward()
        fw.turn_straight()

def setup():
    if calibrate:
        cali()


def getDistance(prevDistance):
    s_10 = 1.4648     # Écart-type pour 10 cm
    n_10 = 100        # Taille de l'échantillon pour 10 cm
    Z_critical = 1.96 # Valeur critique pour un niveau de confiance de 95%
    
    distance = ua.get_distance()
    distance = (distance + prevDistance)/2
    IC_lower_10 = distance - Z_critical * (s_10 / math.sqrt(n_10))
    IC_upper_10 = distance + Z_critical * (s_10 / math.sqrt(n_10))
    
    if(IC_lower_10< prevDistance) and (prevDistance < IC_upper_10):    
        print("distance: %scm" % prevDistance)
        distance = prevDistance

    return distance


def main():
    global turning_angle, targetSens
    global isObstacle
    global isTurnExtremeRight, isTurnExtremeLeft
    global cptTurnExtremeSteps, cptStraightAfterExtremeTurn
    global lastSpeedSens
    global angleLevel, speedLevel

    distance =0
    off_track_count = 0
    bw.speed = lastSpeedSens[0]
    target_speed = 0
    step = 0
    prevDistance =0
    s_10 = 1.4648     # Écart-type pour 10 cm
    n_10 = 100        # Taille de l'échantillon pour 10 cm
    Z_critical = 1.96 # Valeur critique pour un niveau de confiance de 95%
    while True:
        distance = getDistance(distance)
        if(distance < 11):
            prevDistance =1
        else:
            lt_status_now = lf.read_digital()
            
            #### AJUSTE VITESSE ####
            if (lt_status_valid(lt_status_now) and not isObstacle):# ETAT CAPTEUR VALID

                if lt_status_now == [0,0,1,0,0]:

                    if (check_turn_extreme("at_least_one")):
                        cptStraightAfterExtremeTurn = 100 # on part un cpt pour maintenir une faible vitesse pendant les 100 premiers
                                                        # cycle apres un extreme turn
                        fw.turn(90) # Roue normale
                        bw.stop() # Arrête les moteurs pour dire que on a finit EXTREME TURN
                        time.sleep(0.2)
                        lastSpeedSens = (1, "forward") # on ajuste la vitesse a 1 pour accelerer progressivement
                        isTurnExtremeLeft = False
                        isTurnExtremeRight = False

                    if cptStraightAfterExtremeTurn > 0: # tant que on a pas atteint 100
                        target_speed = speedLevel[4]# tres basse vitesse
                        cptStraightAfterExtremeTurn -= 1
                    else: 
                        target_speed = speedLevel[0]
                        step = angleLevel[0]# vitesse normal

            
                    cptTurnExtremeSteps = reset_compteur(cptTurnExtremeSteps)

                elif (check_turn_extreme("not")):

                    if lt_status_now not in ([1,0,0,0,0],[0,0,0,0,1]):
                        if lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
                            step = angleLevel[1]
                            target_speed = speedLevel[1]

                        elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0] :
                            step = angleLevel[2]
                            target_speed = speedLevel[2]

                        elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1] :
                            step = angleLevel[3]
                            target_speed = speedLevel[3]

                    else:
                        #### ACTIVATION EXTREME TURN ####
                        isTurnExtremeLeft = lt_status_now == [1, 0, 0, 0, 0]
                        isTurnExtremeRight = lt_status_now == [0, 0, 0, 0, 1]

            if (check_turn_extreme("at_least_one")):
                    #### EXECUTE EXTREME TURN ####
        
                turnExtreme(isTurnExtremeRight, isTurnExtremeLeft)
            elif (check_turn_extreme("not")):
                    #### AJUSTE ANGLE SI PAS EXTREME TURN ####
                    
                lastSpeedSens = adjust_speed_and_sens(target_speed=target_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
                turning_angle, isTurnExtremeLeft, isTurnExtremeRight, off_track_count = adjust_angle(lt_status_now, turning_angle, isTurnExtremeRight, isTurnExtremeLeft, off_track_count, step)
                fw.turn(turning_angle)
                
            else: # ETAT CAPTEUR NON VALID
                off_track_count = +1

        time.sleep(delay)
        prevDistance = distance 
            
            

def obstacle():
    global cptCompTourneSteps
    global lastSpeedSens
    global targetSens
    global isObstacle
    global speedLevel

    if cptCompTourneSteps[0] > 0:
        fw.turn(90)
        bw.backward()
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[5], lastSpeed=lastSpeedSens[0], increment=5, targetSens="backward", lastSens=lastSpeedSens[1])
        cptCompTourneSteps[0] -= 1
        
    elif cptCompTourneSteps[1] and cptCompTourneSteps[0] == 0 :
        turning_angle = int(90 - angleLevel[4])
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[5], lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneSteps[1] -= 1
        
    elif cptCompTourneSteps[2]  > 0 and cptCompTourneSteps[1] == 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[5], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneSteps[2]  -= 1
        
    elif cptCompTourneSteps[3] > 0 and cptCompTourneSteps[2]  == 0 :
        turning_angle = int(90 + angleLevel[4])
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[5], lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneSteps[3]-= 1
        
    elif cptCompTourneSteps[4] > 0 and cptCompTourneSteps[3]== 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[5], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptCompTourneSteps[4] -= 1
        
    elif cptCompTourneSteps[4] == 0:
        cptCompTourneSteps = reset_compteur_obstacle(cptCompTourneSteps) 
        
def reset_compteur_obstacle(cptCompTourneSteps = [100, 200, 200, 200, 200]):
    cptCompTourneSteps = [100, 200, 200, 200, 200]
    return cptCompTourneSteps

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


def reset_compteur(cptTurnExtremeSteps=[0, 0, 0]):
    cptTurnExtremeSteps = [400, 350, 60]
    return cptTurnExtremeSteps

def check_turn_extreme(mode="none"):
    # verification specifique des cas
    if mode == "not":
        return not isTurnExtremeRight and not isTurnExtremeLeft
    elif mode == "at_least_one":
        return isTurnExtremeRight or isTurnExtremeLeft
    else:
        print("Mode invalide. Utilisez 'not' ou 'at_least_one'.")



def lt_status_valid(lt_status_now):
    # Liste des états valides
    valid_states = [[0, 0, 0, 0, 1],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [1, 0, 0, 0, 0]]
    # Vérifie si lt_status_now est dans la liste des états valides
    return lt_status_now in valid_states
def adjust_speed_and_sens(target_speed=60, lastSpeed=60, increment=10, targetSens="forward", lastSens="forward"):
    # Étape 1 : Si les directions sont différentes, ralentir jusqu'à zéro

    if targetSens != lastSens:
        if lastSpeed > 0:
            lastSpeed = max(lastSpeed - increment, 0)  # Réduire la vitesse progressivement
            #print(lastSpeed)
        elif lastSpeed <= 0:
            lastSpeed = 0
            lastSens = targetSens  # Mettre à jour la direction une fois la vitesse à zéro
            bw.stop()
            time.sleep(0.2)
    # Étape 2 : Si la direction est correcte, ajuster la vitesse pour atteindre
    # la cible
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

def adjust_angle(lt_status_now=[0,0,0,0,0], turning_angle=0, isTurnExtremeRight=False, isTurnExtremeLeft=False, off_track_count=0, step=0):
    #### LEFT ####

    if check_turn_extreme("not"):
        
        if lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0]):
            turning_angle = int(90 - step)
    #### RIGHT ####
        elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1]):
            turning_angle = int(90 + step)
    #### STRAIGHT ####
        elif lt_status_now == [0, 0, 1, 0, 0]:
            fw.turn(90)

    off_track_count = 0
    return turning_angle, isTurnExtremeLeft, isTurnExtremeRight, off_track_count
            
 
def turnExtreme(isTurnExtremeRight=False, isTurnExtremeLeft=False):
     #### PARAMETRE ####
    global cptTurnExtremeSteps
    global angleLevel
    global speedLevel
    global lastSpeedSens 
     #### EXTREME LEFT ####
    if isTurnExtremeLeft and not isTurnExtremeRight:
        """ if cptTurnExtremeSteps[0] == 500 : print("isTurnExtremeLeft    onAvance")
        if cptTurnExtremeSteps[1] == 349 :print("isTurnExtremeLeft    onRecule")
        if cptTurnExtremeSteps[2] == 59: print("isTurnExtremeLeft    onAvanceApresRecule")
        if cptTurnExtremeSteps[2] == 1: print("fin") """
       

        if cptTurnExtremeSteps[0] > 0:
            turning_angle = int(90 - angleLevel[3])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[0] -= 1
            
        elif cptTurnExtremeSteps[1] > 0 and cptTurnExtremeSteps[0] == 0:
            turning_angle = (- (angleLevel[4] - 90) + 90) * fw.turning_max
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=12, targetSens="backward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[1]-= 1
            
        elif cptTurnExtremeSteps[2] > 0 and cptTurnExtremeSteps[1] == 0:
            turning_angle = int(90 - angleLevel[2])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[2] -= 1 


    #### EXTREME RIGHT ####
    elif isTurnExtremeRight and not isTurnExtremeLeft:
        if cptTurnExtremeSteps[0] == 500 : print("isTurnExtremeRight    onAvance")
        if cptTurnExtremeSteps[1] == 349 :print("isTurnExtremeRight    onRecule")
        if cptTurnExtremeSteps[2] == 59: print("isTurnExtremeRight    onAvanceApresRecule")
        if cptTurnExtremeSteps[2] == 1: print("fin")
        
        if cptTurnExtremeSteps[0] > 0:
            turning_angle = int(90 + angleLevel[3])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[0] -= 1
            
        elif cptTurnExtremeSteps[1] > 0 and cptTurnExtremeSteps[0] == 0 :
            turning_angle = (angleLevel[4] - 90) / abs(90 - angleLevel[4]) * fw.turning_max
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=10, targetSens="backward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[1]-= 1
            
        elif cptTurnExtremeSteps[2] > 0 and cptTurnExtremeSteps[1] == 0:
            turning_angle = int(90 + angleLevel[2])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[2] -= 1

    if cptTurnExtremeSteps[2] == 0:   
       cptTurnExtremeSteps = reset_compteur(cptTurnExtremeSteps)
    else:
      fw.turn(turning_angle) 
           



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


