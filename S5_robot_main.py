'''

header

'''
#from S5_robot_line import *
#from S5_robot_line import LineState
import S5_robot_line
from S5_robot_line import *

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
            self.CheckChangeLine()
        elif self.CurrentDrivingState == self.DrivingStateBrake:
            print("placeholder")
        elif self.CurrentDrivingState == self.DrivingStateReverse:
            print("placeholder")
        elif self.CurrentDrivingState == self.DrivingStateObstacle:
            print("placeholder")
        elif self.CurrentDrivingState == self.DrivingStateFinal:
            print("placeholder")
        elif self.CurrentDrivingState == self.DrivingStateLost:
            print("placeholder")
        else: # self.CurrentDrivingState == self.DrivingStateNone:
            self.CurrentDrivingState = self.DrivingStateLost
        return self.CurrentDrivingState

    def CheckChangeLine(self):
        some_variable_from_sensor = 0
        if(some_variable_from_sensor == 1):
            self.CurrentDrivingState = self.DrivingStateBrake


class LineState:
    straight = 0
    reverseRight = -3 # reversing phase of a right turn (wheel point left)
    outerRight = -2
    innerRight = -1
    innerLeft = 1
    outerLeft = 2
    reverseLeft = 3 # reversing phase of a left turn (wheel point right)

    lostRight = -4
    lostLeft = 4


def ModeLineStraight(line_mode, line_sensor):
    new_line_mode = line_mode

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
    SetDriveTarget(60, 0)

    # return the new LineState, or the current one if there's no change
    return new_line_mode

def ModeLineInnerRight(line_mode, line_sensor):
    new_line_mode = line_mode

    # check for next state
    if line_sensor in ([0,0,1,0,0]):
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
    SetDriveTarget(50, 20)

    # return the new LineState, or the current one if there's no change
    return new_line_mode

def ModeLineInnerLeft(line_mode, line_sensor):
    new_line_mode = line_mode

    # check for next state
    if line_sensor in ([0,0,1,0,0]):
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
    SetDriveTarget(50, -20)

    # return the new LineState, or the current one if there's no change
    return new_line_mode

def ModeLineOuterRight(line_mode, line_sensor):
    new_line_mode = int(line_mode)

    # check if line is lost ( this covers the case [0,0,0,0,0] )
    if LineLostCounter > 10: # TODO: replace 10 by a proper timer <-------------
        # the line is lost
        # try to slow down and be ready to reverse
        new_line_mode = LineState.outerRight
        SetDriveTarget(20, 45)
        return new_line_mode
    elif LineLostCounter > 20: # TODO: replace 20 by a proper timer <-------------
        # line is fully lost, change mode
        new_line_mode = LineState.reverseRight
        SetDriveTarget(0, 0)
        return new_line_mode

    # check for next state
    if line_sensor in ([0,0,1,0,0]):
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
    SetDriveTarget(30, 45)

    # return the new LineState, or the current one if there's no change
    return new_line_mode

def ModeLineOuterLeft(line_mode, line_sensor):
    new_line_mode = int(line_mode)

    # check if line is lost ( this covers the case [0,0,0,0,0] )
    if LineLostCounter > 10: # TODO: replace 10 by a proper timer <-------------
        # the line is lost
        # try to slow down and be ready to reverse
        new_line_mode = LineState.outerLeft
        SetDriveTarget(20, -45)
        return new_line_mode
    elif LineLostCounter > 20: # TODO: replace 20 by a proper timer <-------------
        # line is fully lost, change mode
        new_line_mode = LineState.reverseLeft
        SetDriveTarget(0, 0)
        return new_line_mode

    # check for next state
    if line_sensor in ([0,0,1,0,0]):
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
    SetDriveTarget(30, -45)

    # return the new LineState, or the current one if there's no change
    return new_line_mode

def ModeLineReverseRight(line_mode, line_sensor):
    new_line_mode = int(line_mode)

    # LineLostCounter used because it gets reset at the same time we start reversing
    if line_sensor not in ([0,0,0,0,0]):
        # line found
        new_line_mode = LineState.outerRight # good enough state, it will get changed again next loop
        SetDriveTarget(30, 45)
    elif LineLostCounter > 80:
        # start slowing down again
        new_line_mode = LineState.reverseRight
        SetDriveTarget(-20, -30)
    elif LineLostCounter > 100:
        # reversing for long enough, start going forward again
        new_line_mode = LineState.outerRight
        SetDriveTarget(0, 0)
    else:
        # keep reversing
        new_line_mode = LineState.reverseRight
        SetDriveTarget(-30, -45)

    return new_line_mode

def ModeLineReverseLeft(line_mode, line_sensor):
    new_line_mode = int(line_mode)

    # LineLostCounter used because it gets reset at the same time we start reversing
    if line_sensor not in ([0,0,0,0,0]):
        # line found
        new_line_mode = LineState.outerLeft # good enough state, it will get changed again next loop
        SetDriveTarget(30, -45)
    elif LineLostCounter > 80:
        # start slowing down again
        new_line_mode = LineState.reverseLeft
        SetDriveTarget(-20, 30)
    elif LineLostCounter > 100:
        # reversing for long enough, start going forward again
        new_line_mode = LineState.outerLeft
        SetDriveTarget(0, 0)
    else:
        # keep reversing
        new_line_mode = LineState.reverseLeft
        SetDriveTarget(-30, 45)

    return new_line_mode

#----------------------------------------------------------------------------------
# mode Line Follow main function
# called when car is supposed to follow line
# manage the change of inner states
LineLostCounter = 5 # counter of "time" since the line was last seen
LineCurrentMode = LineState.straight
def ModeLineDrive(force_reset=False):
    global LineLostCounter
    global LineCurrentMode
    if force_reset:
        LineCurrentMode = LineState.straight

    new_line_state = LineCurrentMode
    #-----------
    # ok nah screw this, I should have 1 function per possible state
    # and each function should decide on their own
    # how state transition should work
    # --------------

    # get sensor status
    sensor_status = [0,0,1,0,0] # TODO: replace with actual sensor
        # maybe do some check on very important case like [0,0,0,0,0] or [1,1,1,1,1]
    if sensor_status == [0,0,0,0,0]:
        LineLostCounter = LineLostCounter + 1

    # get intended action
    if LineCurrentMode == LineState.straight:
        new_line_state = ModeLineStraight(LineCurrentMode, sensor_status)

    elif LineCurrentMode == LineState.innerRight:
        new_line_state = ModeLineInnerRight(LineCurrentMode, sensor_status)
    elif LineCurrentMode == LineState.outerRight:
        new_line_state = ModeLineOuterRight(LineCurrentMode, sensor_status)

    elif LineCurrentMode == LineState.innerLeft:
        new_line_state = ModeLineInnerLeft(LineCurrentMode, sensor_status)
    elif LineCurrentMode == LineState.outerLeft:
        new_line_state = ModeLineOuterLeft(LineCurrentMode, sensor_status)

    elif LineCurrentMode == LineState.reverseRight:
        new_line_state = ModeLineReverseRight(LineCurrentMode, sensor_status)
    elif LineCurrentMode == LineState.reverseLeft:
        new_line_state = ModeLineReverseLeft(LineCurrentMode, sensor_status)

    # check if state changed
    if new_line_state != LineCurrentMode: # the state has changed
        LineLostCounter = 0 # reset line lost counter

    LineCurrentMode = new_line_state
    return LineCurrentMode

#----------------------------------------------------------------------------------
# main function to move the car every
#
LineFollower = LineState()
def Drive(_drive_mode):
    global LineFollower

    if _drive_mode == DrivingState.DrivingStateLine:
        # call the line-following methode
        print("DrivingStateLine")
        LineFollower.LineDrive()

    elif _drive_mode == DrivingState.DrivingStateBrake:
        # call the braking methode
        print("DrivingStateBrake")


def SetDriveTarget(wheel_speed, wheel_angle):
    print('[ SetDriveTarget() ] target speed: ' + str(wheel_speed) + ' , target angle: ' + str(wheel_angle))
    # call smoothing logic
        # compute speed limit with both current and target steer angle and choose the lowest
    # call actual car function

def InitCar():
    # init picar

    # init global variable
    global LineLostCounter
    LineLostCounter = 0
    global LineCurrentMode
    LineCurrentMode = LineState.straight

if __name__ == '__main__':
    line_state = LineState()
    line_state.TestFunction()
    print('end of test')
    driving_state = DrivingState()
    # get time elapsed

    # update driving mode
    drive_mode = driving_state.CheckDrivingMode()

    # drive the car
    Drive(drive_mode)