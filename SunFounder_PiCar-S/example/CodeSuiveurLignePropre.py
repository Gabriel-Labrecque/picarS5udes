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
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from SunFounder_Line_Follower import Line_Follower
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
REFERENCES = [53.0, 51.5, 27.5, 40.0, 39.0]



# Capteur Ultrason
ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
back_distance = 10
turn_distance = 20
force_turning = 0    # 0 = random direction, 1 = force left, 2 = force right, 3 = orderdly
last_angle = 90
cptObstacleSteps = [100, 200, 200, 200, 200]

isObstacle = False
thread_capteurDistance =0
distance =0






#calibrate = True
calibrate = False
isTurnExtremeLeft, isTurnExtremeRight, isStop, isObstacle = False, False, False, False
forward_speed = 80
backward_speed = 70
turning_angle = 40
cptStraightAfterExtremeTurn = 0
cptStopProgressif = 0
cptTurnExtremeSteps = [400, 250, 100]
angleLevelCroissant = [0, 3, 10, 30, 45]
speedLevel = [50, 45, 40, 35, 30]
lastSpeedSens = (1, "forward") 
cptObstacleSteps = [100, 200, 200, 200, 200]
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

def main():
    global turning_angle, targetSens
    global isTurnExtremeRight, isTurnExtremeLeft, isObstacle, isStop
    global cptTurnExtremeSteps, cptStraightAfterExtremeTurn, cptStopProgressif, cptObstacleSteps
    global lastSpeedSens
    global angleLevelCroissant, speedLevel
    
    
    off_track_count = 0
    bw.speed = lastSpeedSens[0]
    target_speed = 0
    step = 0
    IsStatusLineCaptorValid = False
    distance = 0
    
    while True:
        lt_status_now = lf.read_digital()
        IsStatusLineCaptorValid = lt_status_valid(lt_status_now)
        
        
        distance = getDistance(distance)
        #### ON STOP TOUT ####
        if (lt_status_now == [1,1,1,1,1] and not check_specific_case("isStop")):
            isStop = True
            cptStopProgressif = 100
        
        #### ON AS UN OBSTACLE ####
        if ((distance < 11) and not check_specific_case("isObstacle")) and not isStop:
            isObstacle = True
            
        
        
        if (IsStatusLineCaptorValid and check_specific_case("isNotStop_and_isNotObstacle")):
        # ETAT CAPTEUR VALID

            if lt_status_now == [0,0,1,0,0]:

                if (check_specific_case("at_least_one_extreme_turn")):
                    
                    #### DEFINIR VARIABLE POUR ACCELERATION PROGRESSIVE PENDANT 100 CYCLES ####
                    cptStraightAfterExtremeTurn = reset_compteurs("cptStraightAfterExtremeTurn")
                                                      
                    print("Basse vitesse apres extremeTurn")
                    fw.turn(90) # Roue normale
                    bw.stop() # Arrête les moteurs pour dire que on a finit EXTREME TURN
                    time.sleep(0.2)
                    lastSpeedSens = (1, "forward") #
                    isTurnExtremeLeft = False
                    isTurnExtremeRight = False
                    cptTurnExtremeSteps = reset_compteurs("cptTurnExtremeSteps")
                #### ACCELERATION PROGRESSIVE ####
                if cptStraightAfterExtremeTurn > 0: # tant que on a pas atteint 100
                    target_speed = speedLevel[4]# tres basse vitesse
                    cptStraightAfterExtremeTurn -= 1
                   
                
                #### MOUVEMENT STRAIGHT NORMAL ####
                else: 
                    target_speed = speedLevel[0]
                    turning_angle = angleLevelCroissant[0]
                    
                 

            elif (check_specific_case("not_an_extreme_turn")):
                
                #### PAS EXTREME TURN ACTIVER ENCORE ####
                if lt_status_now not in ([1,0,0,0,0],[0,0,0,0,1]):
                    if lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
                        step = angleLevelCroissant[1]
                        target_speed = speedLevel[1]

                    elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0] :
                        step = angleLevelCroissant[2]
                        target_speed = speedLevel[2]

                    elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1] :
                        step = angleLevelCroissant[3]
                        target_speed = speedLevel[3]

                else:
                    #### ON ACTIVE  EXTREME TURN ####
                    print("active extreme turn)")
                    isTurnExtremeLeft = lt_status_now == [1, 0, 0, 0, 0]
                    isTurnExtremeRight = lt_status_now == [0, 0, 0, 0, 1]



        #### AU MOIN 1 EXTREME TURN ACTIVER PEUT IMPORTE STATUS CAPTEUR####
        if (check_specific_case("at_least_one_extreme_turn") and check_specific_case("isNotStop_and_isNotObstacle")):
            turnExtreme(isTurnExtremeRight, isTurnExtremeLeft)  #### EXECUTE EXTREME TURN ####
        
        #### EXECUTE STOP PEUT IMPORTE STATUS CAPTEUR #### 
        elif(check_specific_case("isStop")):
             stopProgressif()
             
        #### EXECUTE CONTOURNEMENT OBSTACLE PEUT IMPORTE STATUS CAPTEUR ####     
        elif(check_specific_case("isObstacle")):
             obstacle()
             
        #### STATUS CAPTEUR VALID ET PAS DE CAS SPECIFIQUE ####    
        elif (check_specific_case("not_a_specific_case") and IsStatusLineCaptorValid):
            lastSpeedSens = adjust_speed_and_sens(target_speed=target_speed, lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
            turning_angle, off_track_count = adjust_angle(lt_status_now, turning_angle, off_track_count, step)
            fw.turn(turning_angle)
 
                   
        else: #### LOST TRACK ETAT CAPTEUR NON VALID #### 
            off_track_count = +1

        time.sleep(delay)
            
               
 
        #  if lt_status_now == [0,0,0,0,0] and not isTurnExtremeRight and not
        #  isTurnExtremeLeft:
        #    off_track_count += 1
        #    if off_track_count > max_off_track_count:#tmp_angle =
        #    -(turning_angle - 90) + 90
        #        tmp_angle = (turning_angle-90)/abs(90-turning_angle)
        #        tmp_angle *= fw.turning_max
        #        bw.speed = backward_speed
        #        bw.backward()
        #        fw.turn(tmp_angle)
                
        #        lf.wait_tile_center()
        #        bw.stop()

        #        fw.turn(turning_angle)
        #        time.sleep(0.2)
        #        bw.speed = forward_speed
        #        bw.forward()
        #        time.sleep(0.2)
        #

def stopProgressif():
    global cptStopProgressif, isStop, lastSpeedSens
    fw.turn(90)
    target_speed = 0
      
    if cptStopProgressif > cptStopProgressif/2:
        print(lastSpeedSens[0])
        lastSpeedSens = adjust_speed_and_sens(target_speed=target_speed, lastSpeed=lastSpeedSens[0], increment=1, targetSens="forward", lastSens=lastSpeedSens[1])
        cptStopProgressif-= 1
    elif cptStopProgressif == cptStopProgressif/2:
        bw.stop()
        time.sleep(5)
        cptStopProgressif-= 1
    elif (cptStopProgressif < cptStopProgressif/2 and cptStopProgressif > 0):
        bw.forward()
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=30, lastSpeed=lastSpeedSens[0], increment=1, targetSens="forward", lastSens=lastSpeedSens[1])
        cptStopProgressif-= 1
        
    else: isStop = False 

   
def stop():
    bw.stop()
    fw.turn_straight()



def check_specific_case(mode="none"):

    # Verification specifique des cas
    if mode == "not_an_extreme_turn":
        return not isTurnExtremeRight and not isTurnExtremeLeft
    elif mode == "at_least_one_extreme_turn":
        return isTurnExtremeRight or isTurnExtremeLeft
    elif mode == "isStop":
        return isStop
    elif mode == "isObstacle":
        return not isStop and isObstacle
    elif mode == "isNotStop_and_isNotObstacle":
        return not isStop and not isObstacle
    elif mode =="not_a_specific_case":
        return not isStop and not isObstacle and not isTurnExtremeRight and not isTurnExtremeLeft
    else:
        print("Specific case invalide.")






def adjust_speed_and_sens(target_speed=60, lastSpeed=60, increment=10, targetSens="forward", lastSens="forward"):
    
    # Étape 1 : Si les directions sont différentes, ralentir jusqu'à zéro

    if targetSens != lastSens:
        if lastSpeed > 0:
            lastSpeed = max(lastSpeed - increment, 0)  # Réduire la vitesse progressivement
            
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



def adjust_angle(lt_status_now =[0,0,0,0,0], turning_angle=0, off_track_count=0, step=0):
    
    #### LEFT ####    
    if lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0]):
        turning_angle = int(90 - step)
    
    #### RIGHT ####
    elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1]):
        turning_angle = int(90 + step)
    
    #### STRAIGHT ####
    elif lt_status_now == [0, 0, 1, 0, 0]:
        fw.turn(90)

    off_track_count = 0
    return turning_angle, off_track_count
            
 
 
def turnExtreme(isTurnExtremeRight=False, isTurnExtremeLeft=False):
    
    #### PARAMETRE ####
    global cptTurnExtremeSteps
    global angleLevelCroissant
    global speedLevel
    global lastSpeedSens 
    
    #### EXTREME LEFT ####
    if isTurnExtremeLeft and not isTurnExtremeRight:
        if cptTurnExtremeSteps[0] == 500 : print("isTurnExtremeLeft    onAvance")
        if cptTurnExtremeSteps[1] == 349 :print("isTurnExtremeLeft    onRecule")
        if cptTurnExtremeSteps[2] == 59: print("isTurnExtremeLeft    onAvanceApresRecule")
        if cptTurnExtremeSteps[2] == 1: print("fin")
       

        if cptTurnExtremeSteps[0] > 0:
            turning_angle = int(90 - angleLevelCroissant[3])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[0] -= 1
            
        elif cptTurnExtremeSteps[1] > 0 and cptTurnExtremeSteps[0] == 0:
            turning_angle = (- (angleLevelCroissant[4] - 90) + 90) * fw.turning_max
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=12, targetSens="backward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[1]-= 1
            
        elif cptTurnExtremeSteps[2] > 0 and cptTurnExtremeSteps[1] == 0:
            turning_angle = int(90 - angleLevelCroissant[2])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[2] -= 1 


    #### EXTREME RIGHT ####
    elif isTurnExtremeRight and not isTurnExtremeLeft:
        #if cptTurnExtremeSteps[0] == 500 : print("isTurnExtremeRight    onAvance")
        #if cptTurnExtremeSteps[1] == 349 :print("isTurnExtremeRight    onRecule")
        #if cptTurnExtremeSteps[2] == 59: print("isTurnExtremeRight    onAvanceApresRecule")
        #if cptTurnExtremeSteps[2] == 1: print("fin")
        
        if cptTurnExtremeSteps[0] > 0:
            turning_angle = int(90 + angleLevelCroissant[3])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[0] -= 1
            
        elif cptTurnExtremeSteps[1] > 0 and cptTurnExtremeSteps[0] == 0 :
            turning_angle = (angleLevelCroissant[4] - 90) / abs(90 - angleLevelCroissant[4]) * fw.turning_max
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=10, targetSens="backward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[1]-= 1
            
        elif cptTurnExtremeSteps[2] > 0 and cptTurnExtremeSteps[1] == 0:
            turning_angle = int(90 + angleLevelCroissant[2])
            lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=2, targetSens="forward", lastSens=lastSpeedSens[1])
            cptTurnExtremeSteps[2] -= 1

    if cptTurnExtremeSteps[2] == 0:   
       cptTurnExtremeSteps = reset_compteurs("cptTurnExtremeSteps")
    else:
      fw.turn(turning_angle) 
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

    return distance           
def obstacle(distance = 0):
    global cptObstacleSteps, lastSpeedSens, targetSens, isObstacle, speedLevel

    if distance < 30:
        fw.turn(90)
        bw.backward()
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="backward", lastSens=lastSpeedSens[1])
        cptObstacleSteps[0] -= 1
        
    elif cptObstacleSteps[1] > 0 and distance >= 30:
        turning_angle = int(90 - angleLevelCroissant[4])
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptObstacleSteps[1] -= 1
        
    elif cptObstacleSteps[2]  > 0 and cptObstacleSteps[1] == 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptObstacleSteps[2]  -= 1
        
    elif cptObstacleSteps[3] > 0 and cptObstacleSteps[2]  == 0 :
        turning_angle = int(90 + angleLevelCroissant[4])
        fw.turn(turning_angle)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=10, targetSens="forward", lastSens=lastSpeedSens[1])
        cptObstacleSteps[3]-= 1
        
    elif cptObstacleSteps[4] > 0 and cptObstacleSteps[3]== 0:
        fw.turn(90)
        lastSpeedSens = adjust_speed_and_sens(target_speed=speedLevel[4], lastSpeed=lastSpeedSens[0], increment=5, targetSens="forward", lastSens=lastSpeedSens[1])
        cptObstacleSteps[4] -= 1
        
    elif cptObstacleSteps[4] == 0:
        cptObstacleSteps = reset_compteurs("cptObstacleSteps")
        isObstacle = False

        
def reset_compteurs(toReset ="none"):
    global cptObstacleSteps, cptTurnExtremeSteps
   
    if toReset == "cptObstacleSteps":
        cptObstacleSteps = [100, 200, 200, 200, 200]
    elif toReset == "cptTurnExtremeSteps":
        cptTurnExtremeSteps = [400, 350, 60]
    elif toReset == "cptStopProgressif":
        cptStopProgressif = 200
    elif toReset == "cptStraightAfterExtremeTurn":
        cptStraightAfterExtremeTurn = 100  
    else:
        print("toReset invalide. Utilisez 'cptObstacleSteps' ou 'cptTurnExtremeSteps'.")


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


