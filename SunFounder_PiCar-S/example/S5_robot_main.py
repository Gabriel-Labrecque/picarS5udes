'''

header

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

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
lf = Line_Follower.Line_Follower()
ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)

REFERENCES = [30.0, 29.5, 30.0, 34.0, 29.0]
lf.references = REFERENCES
bw.ready()
fw.ready()
fw.turning_max = 45

SensorLine = [0,0,0,0,0]
SensorDistance = 30
SensorDistanceEnable = True

   
def getDistance(prevDistance):
    s_10 = 1.4648     # Écart-type pour 10 cm
    n_10 = 100        # Taille de l'échantillon pour 10 cm
    Z_critical = 1.96 # Valeur critique pour un niveau de confiance de 95%
    
    distance = ua.get_distance()
    distance = (distance + prevDistance)/2 # spike smoothing
    IC_lower_10 = distance - Z_critical * (s_10 / math.sqrt(n_10))
    IC_upper_10 = distance + Z_critical * (s_10 / math.sqrt(n_10))
    
    if(IC_lower_10 < prevDistance) and (prevDistance < IC_upper_10):    
        #print("distance: %scm" % prevDistance)
        distance = prevDistance

    return distance

def UpdateSensor():
    global SensorLine, SensorDistance, SensorDistanceEnable
    SensorLine = lf.read_digital()

    if SensorDistanceEnable:
        SensorDistance = getDistance(SensorDistance)


GlobalPrint = True
def myprint(text, verbose=1):
    # verbose 0=off, 1=on, 2=forced
    global GlobalPrint
    if (verbose==2):
        print(text)
    elif (verbose==1) and GlobalPrint:
        print(text)
    

class LineState:
    straight = 0
    reverseRight = -3 # reversing phase of a right turn (wheel point left)
    outerRight = -2
    innerRight = -1
    innerLeft = 1
    outerLeft = 2
    reverseLeft = 3 # reversing phase of a left turn (wheel point right)
    tee = 10 # found the T, stop the car

    TargetSpeed = 0
    TargetAngle = 0
    LineLostTimer = 5 # time since the line was last seen
    LineFoundCounter = 0
    CurrentMode = straight

    def __init__(self):
        self.LineLostTimer = 0
        self.LineFoundCounter = 0
        self.CurrentMode = self.straight

    def SetDriveTarget(self, _speed, _angle):
        self.TargetSpeed = _speed
        self.TargetAngle = _angle
    
    def ForceState(self, new_state):
        self.CurrentMode = int(new_state)

    def LineDrive(self, dt=0.1, force_reset=False):
        global SensorLine
        if force_reset:
            self.CurrentMode = LineState.straight

        new_line_state = int(self.CurrentMode)
        # -----------
        # ok nah screw this, I should have 1 function per possible state
        # and each function should decide on their own
        # how state transition should work
        # --------------

        # get sensor status
        sensor_status = SensorLine # read the line follower sensor

            # maybe do some check on very important case like [0,0,0,0,0] or [1,1,1,1,1]
        if sensor_status == [0,0,0,0,0]:
            self.LineLostTimer = self.LineLostTimer + dt
            self.LineFoundCounter = 0
        elif self.LineFoundCounter > 3: # seen a line for X cycle in a row
            self.LineLostTimer = 0 # line not lost anymore so reset LineLostTimer
            self.LineFoundCounter = 0
        else:
            self.LineFoundCounter = self.LineFoundCounter + 1
        
        # get intended action
        if self.CurrentMode == LineState.straight:
            new_line_state = self.ModeStraight(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.innerRight:
            new_line_state = self.ModeInnerRight(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.innerLeft:
            new_line_state = self.ModeInnerLeft(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.outerRight:
            new_line_state = self.ModeOuterRight(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.outerLeft:
            new_line_state = self.ModeOuterLeft(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.reverseRight:
            new_line_state = self.ModeReverseRight(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.reverseLeft:
            new_line_state = self.ModeReverseLeft(self.CurrentMode, sensor_status)

        # check if state changed
        myprint('new state: ' + str(new_line_state) + ' , old state: ' + str(self.CurrentMode))
        if new_line_state != self.CurrentMode: # the state has changed
            self.LineLostTimer = 0 # reset line lost counter
            self.LineFoundCounter = 0
        myprint('line lost for ' + str(self.LineLostTimer) + ' cycle')

        self.CurrentMode = new_line_state
        return self.CurrentMode
    
        
    def ModeStraight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check for next state
        if line_sensor in ([0,0,1,0,0],[0,0,0,0,0]):
            new_line_mode = LineState.straight
        elif line_sensor in ([0,0,0,1,0],[0,0,1,1,0]):
            new_line_mode = LineState.innerRight
        elif line_sensor in ([0,0,0,0,1],[0,0,0,1,1],[0,0,1,1,1]):
            new_line_mode = LineState.outerRight
        elif line_sensor in ([0,1,0,0,0],[0,1,1,0,0]):
            new_line_mode = LineState.innerLeft
        elif line_sensor in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
            new_line_mode = LineState.outerLeft

        # move the car
        self.SetDriveTarget(50, 0)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeInnerRight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check for next state
        if line_sensor == [0,0,1,0,0]:
            new_line_mode = LineState.straight
        elif line_sensor in ([0,0,0,1,0],[0,0,1,1,0],[0,0,0,0,0]):
            new_line_mode = LineState.innerRight
        elif line_sensor in ([0,0,0,0,1],[0,0,0,1,1],[0,0,1,1,1]):
            new_line_mode = LineState.outerRight
        elif line_sensor in ([0,1,0,0,0],[0,1,1,0,0]):
            new_line_mode = LineState.innerLeft
        elif line_sensor in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
            new_line_mode = LineState.outerLeft

        # move the car
        self.SetDriveTarget(50, 20)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeInnerLeft(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check for next state
        if line_sensor == [0,0,1,0,0]:
            new_line_mode = LineState.straight
        elif line_sensor in ([0,0,0,1,0],[0,0,1,1,0]):
            new_line_mode = LineState.innerRight
        elif line_sensor in ([0,0,0,0,1],[0,0,0,1,1],[0,0,1,1,1]):
            new_line_mode = LineState.outerRight
        elif line_sensor in ([0,1,0,0,0],[0,1,1,0,0],[0,0,0,0,0]):
            new_line_mode = LineState.innerLeft
        elif line_sensor in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
            new_line_mode = LineState.outerLeft

        # move the car
        self.SetDriveTarget(50, -20)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeOuterRight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check if line is lost ( this covers the case [0,0,0,0,0] )
        if 3 < self.LineLostTimer < 5: # slow down after 3 sec 
            # the line is lost
            # try to slow down and be ready to reverse
            myprint('change state OuterRight->OuterRight')
            new_line_mode = LineState.outerRight
            self.SetDriveTarget(30, 45)
            return new_line_mode
        elif self.LineLostTimer >= 5: # start revesing after 5 sec
            # line is fully lost, change mode
            myprint('change state OuterRight->reverseRight <-----')
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(0, 0)
            return new_line_mode

        # check for next state
        if line_sensor == [0,0,1,0,0]:
            new_line_mode = LineState.straight
        elif line_sensor in ([0,0,0,1,0],[0,0,1,1,0]):
            new_line_mode = LineState.innerRight
        elif line_sensor in ([0,0,0,0,1],[0,0,0,1,1],[0,0,1,1,1]):
            new_line_mode = LineState.outerRight
        elif line_sensor in ([0,1,0,0,0],[0,1,1,0,0]):
            new_line_mode = LineState.innerLeft
        elif line_sensor in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
            new_line_mode = LineState.outerLeft

        # move the car
        self.SetDriveTarget(40, 45)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeOuterLeft(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check if line is lost ( this covers the case [0,0,0,0,0] )
        if 3 < self.LineLostTimer < 5: # slow down after 3 sec 
            # the line is lost
            # try to slow down and be ready to reverse
            myprint('change state OuterLeft->OuterLeft')
            new_line_mode = LineState.outerLeft
            self.SetDriveTarget(30, -45)
            return new_line_mode
        elif self.LineLostTimer >= 5: # start revesing after 5 sec
            # line is fully lost, change mode
            myprint('change state OuterLeft->reverseLeft <------')
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(0, 0)
            return new_line_mode

        # check for next state
        if line_sensor == [0,0,1,0,0]:
            new_line_mode = LineState.straight
        elif line_sensor in ([0,0,0,1,0],[0,0,1,1,0]):
            new_line_mode = LineState.innerRight
        elif line_sensor in ([0,0,0,0,1],[0,0,0,1,1],[0,0,1,1,1]):
            new_line_mode = LineState.outerRight
        elif line_sensor in ([0,1,0,0,0],[0,1,1,0,0]):
            new_line_mode = LineState.innerLeft
        elif line_sensor in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
            new_line_mode = LineState.outerLeft

        # move the car
        self.SetDriveTarget(40, -45)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeReverseRight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # LineLostCounter used because it gets reset at the same time we start reversing
        if line_sensor != [0,0,0,0,0]:
            # line found
            new_line_mode = LineState.outerRight # good enough state, it will get changed again next loop
            self.SetDriveTarget(0, 0)
        elif self.LineLostTimer < 100:
            # keep reversing
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(-40, -45)
        elif self.LineLostTimer < 150:
            # start slowing down again
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(-30, -30)
        elif self.LineLostTimer >= 150:
            # reversing for long enough, start going forward again
            new_line_mode = LineState.outerRight
            self.SetDriveTarget(0, 0)
        else:
            # keep reversing
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(-40, -45)

        return new_line_mode

    def ModeReverseLeft(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # LineLostCounter used because it gets reset at the same time we start reversing
        if line_sensor != [0,0,0,0,0]:
            # line found
            new_line_mode = LineState.outerLeft # good enough state, it will get changed again next loop
            self.SetDriveTarget(0, 0)
        elif self.LineLostTimer < 100:
            # keep reversing
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(-40, 45)
        elif self.LineLostTimer < 150:
            # start slowing down again
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(-30, 30)
        elif self.LineLostTimer >= 150:
            # reversing for long enough, start going forward again
            new_line_mode = LineState.outerLeft
            self.SetDriveTarget(0, 0)
        else:
            # keep reversing
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(-40, 45)

        return new_line_mode

class BrakeState:
    BrakeComplete = False
    TargetSpeed = 0
    DistanceToWall = 100

    def BrakeDrive(self, dt=0.1, force_reset=False):
        # read sensor
        global SensorDistance
        self.DistanceToWall = SensorDistance

        # PLACEHOLDER CODE
        if self.DistanceToWall > 10:
            self.TargetSpeed = 30 + ( 0.5 * self.DistanceToWall)
        elif self.DistanceToWall <= 10:
            self.TargetSpeed = 0
    
    def CheckFinal(self): # UNSUED, TO BE DELETED
        global LastSpeed
        success1 = False
        success2 = False
        if 8 < self.DistanceToWall < 12: # proper distance to wall
            success1 = True
        if -10 < LastSpeed < 10: # car stopped
            success2 = True
        
        self.BrakeComplete = success1 and success2
    
class ReverseState:
    TargetSpeed = 0
    DistanceToWall = 0

    def ReverseDrive(self):
        global SensorDistance
        self.DistanceToWall = SensorDistance
        # PLACEHOLDER CODE
        if self.DistanceToWall < 20:
            self.TargetSpeed = -30 
        elif self.DistanceToWall >= 20:
            self.TargetSpeed = 0

class ObstacleState:
    TimePassed = 0
    StepProgress = 0
    
    TargetSpeed = 0
    TargetAngle = 0

    def ObstacleDrive(self, dt=0.1):
        self.TimePassed = self.TimePassed + dt

        if self.TimePassed < 10:
            # ----- TURN 1 -----
            self.TargetSpeed = 40
            self.TargetAngle = 45

        elif self.TimePassed < 20:
            # ----- TURN 2 -----
            self.TargetSpeed = 40
            self.TargetAngle = -45

        elif self.TimePassed < 30:
            # ----- TURN 3 -----
            self.TargetSpeed = 40
            self.TargetAngle = -30


class DrivingState:
    DrivingStateLine = 0
    DrivingStateBrake = 1
    DrivingStateReverse = 2
    DrivingStateObstacle = 3
    DrivingStateFinal = 4
    DrivingStateLost = 5
    DrivingStateNone = -1  #

    CurrentDrivingState = DrivingStateLost
    def CheckDrivingMode(self):
        if self.CurrentDrivingState == self.DrivingStateLine:
            myprint("DrivingStateLine")
            self.CheckChangeLine()

        elif self.CurrentDrivingState == self.DrivingStateBrake:
            myprint("DrivingStateBrake")
            self.CheckChangeBrake()

        elif self.CurrentDrivingState == self.DrivingStateReverse:
            myprint("DrivingStateReverse")
            self.CheckChangeReverse() # TODO <----------------------

        elif self.CurrentDrivingState == self.DrivingStateObstacle:
            myprint("DrivingStateObstacle")
            self.CheckChangeObstacle()

        elif self.CurrentDrivingState == self.DrivingStateFinal:
            myprint("DrivingStateFinal")
            # TODO <----------------------

        elif self.CurrentDrivingState == self.DrivingStateLost:
            myprint("DrivingStateLost")
            self.CurrentDrivingState = self.DrivingStateLine

        else: # self.CurrentDrivingState == self.DrivingStateNone:
            self.CurrentDrivingState = self.DrivingStateLine

        return self.CurrentDrivingState

    def CheckChangeLine(self):
        global SensorLine, SensorDistance, SensorDistanceEnable

        if SensorLine == [1,1,1,1,1]:
            self.CurrentDrivingState = self.DrivingStateFinal
            myprint('CHANGED STATE TO FINAL (from line follow)', 2)
        elif SensorDistanceEnable and (SensorDistance < 30): # obstacle seen within 30cm
            self.CurrentDrivingState = self.DrivingStateBrake

    def CheckChangeBrake(self):
        global SensorDistance, LastSpeed
        good_distance = False
        good_speed = False
        
        if 8 < SensorDistance < 12: # proper distance to wall
            good_distance = True
        if -10 < LastSpeed < 10: # car stopped
            good_speed = True
        
        if good_distance and good_speed:
            self.CurrentDrivingState = self.DrivingStateReverse

    def CheckChangeReverse(self):
        global SensorDistance, LastSpeed, SensorDistanceEnable
        good_distance = False
        good_speed = False

        if 18 < SensorDistance < 22: # proper distance to wall
            good_distance = True
        if -10 < LastSpeed < 10: # car stopped
            good_speed = True
        
        if good_distance and good_speed:
            SensorDistanceEnable = False
            self.CurrentDrivingState = self.DrivingStateReverse


    def CheckChangeObstacle(self):
        global SensorLine, SensorDistanceEnable
        if SensorLine != [0,0,0,0,0]: # line found
            SensorDistanceEnable = False
            self.CurrentDrivingState = self.DrivingStateLine

#----------------------------------------------------------------------------------
# main function to move the car every
#
ModeLineFollower = LineState()
ModeBrake = BrakeState()
ModeReverse = ReverseState()
ModeObstacle = ObstacleState()

def Drive(_drive_mode, delta_t):
    global ModeLineFollower, ModeBrake, ModeReverse, ModeObstacle

    if _drive_mode == DrivingState.DrivingStateLine:
        # call the line-following methode
        # myprint("Drive(): DrivingStateLine")
        ModeLineFollower.LineDrive(dt=delta_t)
        target_speed = ModeLineFollower.TargetSpeed
        target_angle = ModeLineFollower.TargetAngle
        SetDriveTarget(target_speed, target_angle, delta_t)

    elif _drive_mode == DrivingState.DrivingStateBrake:
        ModeLineFollower.LineDrive(dt=delta_t)
        ModeBrake.BrakeDrive()
        target_speed = ModeBrake.TargetSpeed # speed from brake
        target_angle = ModeLineFollower.TargetAngle # direction from line
        # call the braking methode
            # keep the line follower to control wheel angle
            # control wheel speed with distance sensor
        SetDriveTarget(target_speed, target_angle, delta_t)
        myprint("Drive(): placeholder DrivingStateBrake")
        
    elif _drive_mode == DrivingState.DrivingStateReverse:
        ModeReverse.ReverseDrive()
        target_speed = ModeReverse.TargetSpeed # speed from brake
        target_angle = 0 # go straight
        SetDriveTarget(target_speed, target_angle, delta_t)
        myprint("Drive(): placeholder DrivingStateReverse")

    elif _drive_mode == DrivingState.DrivingStateObstacle:
        ModeObstacle.ObstacleDrive()
        target_speed = ModeObstacle.TargetSpeed
        target_angle = ModeObstacle.TargetAngle
        ModeLineFollower.ForceState(LineState.outerRight) # prime the line follower to turn in the right direction
        SetDriveTarget(target_speed, target_angle, delta_t)
        myprint("Drive(): placeholder DrivingStateObstacle")

    elif _drive_mode == DrivingState.DrivingStateFinal:
        target_speed = 0
        target_angle = 0
        SetDriveTarget(0, 0, delta_t)
        myprint("Drive(): placeholder DrivingStateFinal")

    elif _drive_mode == DrivingState.DrivingStateLost:
        myprint("Drive(): placeholder DrivingStateLost")

#TempSpeedBuffer = 0
#TempAngleBuffer = 90
LastSpeed = 0
LastAngle = 0
def SetDriveTarget(wheel_speed, wheel_angle, delta_t):
    #global TempSpeedBuffer, TempAngleBuffer
    global LastSpeed, LastAngle

    myprint('[ SetDriveTarget() ] target speed: ' + str(wheel_speed) + ' , target angle: ' + str(wheel_angle))
    # call smoothing logic
        # compute speed limit with both current and target steer angle and choose the lowest
    
    ComputeAccel(wheel_speed, wheel_angle, delta_t)
    smooth_speed = int(LastSpeed)
    smooth_angle = int(LastAngle)

    direction = 0
    if smooth_speed > 0: direction = 1
    elif smooth_speed < 0: direction = -1
    if smooth_speed < -99: smooth_speed = -99
    if smooth_speed > 99: smooth_speed = 99

    # call actual car function
    if direction == 0:
        bw.speed = 0
        bw.stop()
    elif direction > 0:
        bw.speed = smooth_speed
        bw.forward()
    else:
        bw.speed = abs( smooth_speed )
        bw.backward()

    fw.turn(ParseTurn(smooth_angle))

def ComputeAccel(wheel_speed, wheel_angle, delta_t):
    global LastSpeed, LastAngle
    CORRECTION_RATE = 0.05

    step_limit_speed = CORRECTION_RATE / delta_t # move a base amount every cycle
    step_limit_angle = 2.0 * CORRECTION_RATE / delta_t # move a base amount every cycle

    # limit acceleration when turning a lot
    # step_limit_speed = step_limit_speed * abs(math.sin( math.radians(LastAngle) ) ) # TODO: THIS CAUSE ERRORS <------------
    # limit wheel angle turn when going fast (0.5 at full speed, 1.0 at no speed)
    step_limit_angle = step_limit_angle * ((50 + abs(LastSpeed / 2)) / 100) 

    speed_delta = wheel_speed - LastSpeed
    if speed_delta < (0-step_limit_speed): speed_delta = 0 - step_limit_speed
    if speed_delta > (0+step_limit_speed): speed_delta = 0 + step_limit_speed

    angle_delta = wheel_angle - LastAngle
    if angle_delta < (0-step_limit_angle): angle_delta = 0 - step_limit_angle
    if angle_delta > (0+step_limit_angle): angle_delta = 0 + step_limit_angle

    LastSpeed = LastSpeed + speed_delta
    LastAngle = LastAngle + angle_delta
    myprint('New speed: ' + str(LastSpeed) + ' , speed_delta: ' + str(speed_delta))
    myprint('New angle: ' + str(LastAngle) + ' , angle_delta: ' + str(angle_delta))

def ParseTurn(angle):
    # TODO: account for the wheel not being at 45 when you tell them to
    return int(90 + angle)

def InitCar():
    # init picar
    bw.speed = 0
    bw.stop()
    fw.turn(90)
    # init global variable
    global ModeLineFollower
    ModeLineFollower.CurrentMode = LineState.straight

    global SensorDistanceEnable
    SensorDistanceEnable = True

def TerminateCar():
    bw.speed = 0
    bw.stop()
    fw.turn(90)
    
    global SensorDistanceEnable
    SensorDistanceEnable = False


if __name__ == '__main__':
    initial_time = 0
    try:
        initial_time = time.monotonic()
    except Exception as e:
        print('ERROR CATCHED: ')
        print(e)
        TerminateCar()
        print('--- CLOCK IS BROKEN ---')

    try:
        driving_state = DrivingState()
        InitCar()
        #last_time = time.process_time()
        #delta_t = last_time # delta time
        
        last_time = float(initial_time)

        while(True):
            # read from sensors


            # get time elapsed
            delta_t = 0.1
            if initial_time != 0:
                new_time = time.monotonic()
                delta_t = new_time - last_time
                last_time = float(new_time)

            # update driving mode
            drive_mode = driving_state.CheckDrivingMode()

            # drive the car
            Drive(drive_mode, delta_t)
    except Exception as e:
        print('ERROR CATCHED: ')
        print(e)
        TerminateCar()
    except KeyboardInterrupt:
        TerminateCar()
