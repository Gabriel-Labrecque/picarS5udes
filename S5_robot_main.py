'''

header

'''

class LineState:
    straight = 0
    reverseRight = -3 # reversing phase of a right turn (wheel point left)
    outerRight = -2
    innerRight = -1
    innerLeft = 1
    outerLeft = 2
    reverseLeft = 3 # reversing phase of a left turn (wheel point right)

    TargetSpeed = 0
    TargetAngle = 0
    LineLostCounter = 5 # counter of "time" since the line was last seen
    CurrentMode = straight

    def __init__(self):
        self.LineLostCounter = 0
        self.CurrentMode = self.straight

    def SetDriveTarget(self, _speed, _angle):
        self.TargetSpeed = _speed
        self.TargetAngle = _angle
    
    def LineDrive(self, force_reset=False):
        if force_reset:
            self.CurrentMode = LineState.straight

        new_line_state = self.CurrentMode
        #-----------
        # ok nah screw this, I should have 1 function per possible state
        # and each function should decide on their own
        # how state transition should work
        # --------------

        # get sensor status
        sensor_status = [0,0,1,0,0] # TODO: replace with actual sensor
            # maybe do some check on very important case like [0,0,0,0,0] or [1,1,1,1,1]
        if sensor_status == [0,0,0,0,0]:
            self.LineLostCounter = self.LineLostCounter + 1

        # get intended action
        if self.CurrentMode == LineState.straight:
            new_line_state = self.ModeStraight(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.innerRight:
            new_line_state = self.ModeInnerRight(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.outerRight:
            new_line_state = self.ModeOuterRight(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.innerLeft:
            new_line_state = self.ModeInnerLeft(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.outerLeft:
            new_line_state = self.ModeOuterLeft(self.CurrentMode, sensor_status)

        elif self.CurrentMode == LineState.reverseRight:
            new_line_state = self.ModeReverseRight(self.CurrentMode, sensor_status)
        elif self.CurrentMode == LineState.reverseLeft:
            new_line_state = self.ModeReverseLeft(self.CurrentMode, sensor_status)

        # check if state changed
        if new_line_state != self.CurrentMode: # the state has changed
            self.LineLostCounter = 0 # reset line lost counter

        self.CurrentMode = new_line_state
        return self.CurrentMode
    
        
    def ModeStraight(self, line_mode, line_sensor):
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
        self.SetDriveTarget(60, 0)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeInnerRight(self, line_mode, line_sensor):
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
        self.SetDriveTarget(50, 20)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeInnerLeft(self, line_mode, line_sensor):
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
        self.SetDriveTarget(50, -20)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeOuterRight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check if line is lost ( this covers the case [0,0,0,0,0] )
        if self.LineLostCounter > 10: # TODO: replace 10 by a proper timer <-------------
            # the line is lost
            # try to slow down and be ready to reverse
            new_line_mode = LineState.outerRight
            self.SetDriveTarget(20, 45)
            return new_line_mode
        elif self.LineLostCounter > 20: # TODO: replace 20 by a proper timer <-------------
            # line is fully lost, change mode
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(0, 0)
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
        self.SetDriveTarget(30, 45)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeOuterLeft(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # check if line is lost ( this covers the case [0,0,0,0,0] )
        if self.LineLostCounter > 10: # TODO: replace 10 by a proper timer <-------------
            # the line is lost
            # try to slow down and be ready to reverse
            new_line_mode = LineState.outerLeft
            self.SetDriveTarget(20, -45)
            return new_line_mode
        elif self.LineLostCounter > 20: # TODO: replace 20 by a proper timer <-------------
            # line is fully lost, change mode
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(0, 0)
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
        self.SetDriveTarget(30, -45)

        # return the new LineState, or the current one if there's no change
        return new_line_mode

    def ModeReverseRight(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # LineLostCounter used because it gets reset at the same time we start reversing
        if line_sensor not in ([0,0,0,0,0]):
            # line found
            new_line_mode = LineState.outerRight # good enough state, it will get changed again next loop
            self.SetDriveTarget(30, 45)
        elif self.LineLostCounter > 80:
            # start slowing down again
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(-20, -30)
        elif self.LineLostCounter > 100:
            # reversing for long enough, start going forward again
            new_line_mode = LineState.outerRight
            self.SetDriveTarget(0, 0)
        else:
            # keep reversing
            new_line_mode = LineState.reverseRight
            self.SetDriveTarget(-30, -45)

        return new_line_mode

    def ModeReverseLeft(self, line_mode, line_sensor):
        new_line_mode = int(line_mode)

        # LineLostCounter used because it gets reset at the same time we start reversing
        if line_sensor not in ([0,0,0,0,0]):
            # line found
            new_line_mode = LineState.outerLeft # good enough state, it will get changed again next loop
            self.SetDriveTarget(30, -45)
        elif self.LineLostCounter > 80:
            # start slowing down again
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(-20, 30)
        elif self.LineLostCounter > 100:
            # reversing for long enough, start going forward again
            new_line_mode = LineState.outerLeft
            self.SetDriveTarget(0, 0)
        else:
            # keep reversing
            new_line_mode = LineState.reverseLeft
            self.SetDriveTarget(-30, 45)

        return new_line_mode

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

#----------------------------------------------------------------------------------
# main function to move the car every
#
ModeLineFollower = LineState()

def Drive(_drive_mode):
    global ModeLineFollower

    if _drive_mode == DrivingState.DrivingStateLine:
        # call the line-following methode
        print("Drive(): DrivingStateLine")
        ModeLineFollower.LineDrive()
        target_speed = ModeLineFollower.TargetSpeed
        target_angle = ModeLineFollower.TargetAngle
        SetDriveTarget(target_speed, target_angle)

    elif _drive_mode == DrivingState.DrivingStateBrake:
        # call the braking methode
        print("Drive(): placeholder DrivingStateBrake")
        
    elif _drive_mode == DrivingState.DrivingStateReverse:
        print("Drive(): placeholder DrivingStateReverse")
    elif _drive_mode == DrivingState.DrivingStateObstacle:
        print("Drive(): placeholder DrivingStateObstacle")
    elif _drive_mode == DrivingState.DrivingStateFinal:
        print("Drive(): placeholder DrivingStateFinal")
        SetDriveTarget(0, 0)
    elif _drive_mode == DrivingState.DrivingStateLost:
        print("Drive(): placeholder DrivingStateLost")


def SetDriveTarget(wheel_speed, wheel_angle):
    print('[ SetDriveTarget() ] target speed: ' + str(wheel_speed) + ' , target angle: ' + str(wheel_angle))
    # call smoothing logic
        # compute speed limit with both current and target steer angle and choose the lowest
    # call actual car function

def InitCar():
    # init picar

    # init global variable
    global ModeLineFollower
    ModeLineFollower.CurrentMode = LineState.straight

if __name__ == '__main__':
    driving_state = DrivingState()
    InitCar()

    while(True):
        # get time elapsed
        
        # update driving mode
        drive_mode = driving_state.CheckDrivingMode()

        # drive the car
        Drive(drive_mode)