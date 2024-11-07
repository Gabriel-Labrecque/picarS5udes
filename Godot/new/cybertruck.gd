extends Node3D


enum States{
	Line_Following,
	Three_point_turn,
	Obstacle_Avoidance
}

enum ObstacleStates{
	Stop,
	Reculer,
	Turning_away,
	Straight,
	Contour,
	Turning_back,
	Finding_line
	
}

# Constantes

const MAX_OFF_TRACK_COUNT = 10
const OBSTACLE_STOP_DISTANCE = 3.0
const RECOVERY_DISTANCE = 3.0
const DECELERATION_SPEED = 1
var rotation_counter = 0
const ROTATION_THRESHOLD = 2
const FORWARD_SPEED = 0.25
const SLIGHT_SPEED =  0.25
const MIDDLE_SPEED =  0.16
const STRONG_SPEED = 0.07
const EXTREME_SPEED =  0.05
const SLIGHT_TURN = 15.0
const MIDDLE_TURN = 16.0
const STRONG_TURN = 22.0
const EXTREME_TURN = 36.0
# Capteurs
var left_sensor: RayCast3D
var center_sensor: RayCast3D
var right_sensor: RayCast3D
var center_left_sensor: RayCast3D
var center_right_sensor: RayCast3D
var obstacle_sensor: RayCast3D
var front_wheel_angle = 0.0
var rear_wheel_speed = 0.0
var off_track_count = 0
var avance = false
var previous_sensor_side = ""
var pending_rotation_angle = 0.0
var sensor_state = [null, null, null, null, null]
var previousDirectionZ = 0.0
var previousDirectionX = 0.0
var previousDirection = Vector3.ZERO
var previous_angle = 0.0
var state = ""
var side = ""
var ObstacleCount = 0
var compteurStraight = 0
var iscompteurRecule = false
var isObstacleCount = false
var iscompteurStraight = false
var centerValueActivated = false
var pasfinit = true
var is_avoiding = false

var sub_state = ObstacleStates.Stop
var straight_count = 0;
var rot_count = 0;
var return_rot_count = 0;
var current_state = States.Line_Following


var distance = 0
var degre_rot = 0
var degre_initial = 0

func _ready():
	left_sensor = $"Suiveur_ligne/LeftSensor"
	center_sensor = $"Suiveur_ligne/CenterSensor"
	right_sensor = $"Suiveur_ligne/RightSensor"
	center_left_sensor = $"Suiveur_ligne/CenterLeftSensor"
	center_right_sensor = $"Suiveur_ligne/CenterRightSensor"
	obstacle_sensor = $"Obstacle"
	

	
	# Activer les capteurs
	left_sensor.enabled = true
	center_sensor.enabled = true
	right_sensor.enabled = true
	center_left_sensor.enabled = true
	center_right_sensor.enabled = true
	obstacle_sensor.enabled = true
	
	set_process(true)

func _process(delta):
	
	
	
	
	var left_value = left_sensor.is_colliding()
	var center_value = center_sensor.is_colliding()
	var right_value = right_sensor.is_colliding()
	var center_left_value = center_left_sensor.is_colliding()
	var center_right_value = center_right_sensor.is_colliding()
	var obstacle_value = obstacle_sensor.is_colliding()
	sensor_state = [left_value, center_left_value, center_value, center_right_value, right_value]
	centerValueActivated = center_value 
	
	change_state(obstacle_value)
	
	
	if(current_state == States.Obstacle_Avoidance):
		
		var next_state = ObstacleStates.Stop	
		
		if sub_state == ObstacleStates.Stop:
			next_state = ObstacleStates.Reculer
			
		elif  sub_state == ObstacleStates.Reculer and obstacle_sensor.is_colliding():
			next_state = ObstacleStates.Reculer
		elif sub_state == ObstacleStates.Reculer :
			degre_rot = degre_initial
			next_state = ObstacleStates.Turning_away
		elif sub_state == ObstacleStates.Turning_away and (obstacle_sensor.is_colliding() or degre_rot < degre_initial + 45) :
			next_state = ObstacleStates.Turning_away
		elif sub_state == ObstacleStates.Turning_away :
			distance = 0
			next_state = ObstacleStates.Straight
		elif sub_state == ObstacleStates.Straight and distance < 0.5 :
			next_state = ObstacleStates.Straight
		elif sub_state == ObstacleStates.Straight :
			distance =0
			next_state = ObstacleStates.Contour
		elif sub_state == ObstacleStates.Contour and distance < 0.5:
			next_state = ObstacleStates.Contour
		elif sub_state == ObstacleStates.Contour :
			next_state = ObstacleStates.Turning_back
		elif sub_state == ObstacleStates.Turning_back and degre_rot >0 :
			next_state = ObstacleStates.Turning_back
		elif sub_state == ObstacleStates.Turning_back :
			next_state = ObstacleStates.Finding_line 
		elif sub_state == ObstacleStates.Finding_line and obstacle_sensor.is_colliding() :
			next_state = ObstacleStates.Turning_away
		else :
			next_state = ObstacleStates.Finding_line
		
		match sub_state :
			ObstacleStates.Stop:
				advance2(delta,0,'none','none',[false,false,true,false,false])
				print("stop")
				
			ObstacleStates.Reculer:
				obstacle_sensor.target_position = Vector3(0,0.3,0)
				follow_line(delta,sensor_state,-1)
				print('reculer')
			ObstacleStates.Turning_away : 
				rotation(delta,SLIGHT_SPEED,deg_to_rad(SLIGHT_TURN),'left','left',false)
				degre_rot += delta*SLIGHT_TURN
				#print('turning away, deg rot = ',degre_rot)
			ObstacleStates.Straight :
				obstacle_sensor.target_position = Vector3(0,0.1,0)
				advance2(delta,FORWARD_SPEED,'straight','straight',[false,false,true,false,false])
				distance += delta*FORWARD_SPEED
				print("straight")
			ObstacleStates.Contour :
				
				if degre_rot >= 45/2 :
					rotation(delta,SLIGHT_SPEED,deg_to_rad(SLIGHT_TURN),'right','right',false)
					degre_rot -= delta*SLIGHT_TURN/2
					print("contour rot = ", degre_rot)
				else :
					advance2(delta,FORWARD_SPEED,'straight','straight',[false,false,true,false,false])
					distance += delta*FORWARD_SPEED
					print("contour fwd ")
			ObstacleStates.Turning_back :
				rotation(delta,SLIGHT_SPEED,deg_to_rad(SLIGHT_TURN),'right','right',false)
				degre_rot -= delta*SLIGHT_TURN/2
				#print("turning back deg rot  =",degre_rot)
			ObstacleStates.Finding_line :
				if sensor_state.find(true) != -1 :  # si un capteur de ligne trigger, changer en suiveur de ligne
					current_state = States.Line_Following
					print('found the line')
					return
				else : 
					advance2(delta,SLIGHT_SPEED,'none','none',[false,false,true,false,false])

				
		sub_state = next_state
		return

	
	"""if obstacle_value and not isObstacleCount:
		
		isObstacleCount= true
		ObstacleCount = 1
		front_wheel_angle = MIDDLE_TURN
		rear_wheel_speed = MIDDLE_SPEED
		state = "middle"
		side = "left"
		avance = true
		handle_obstacle_avoidance(delta, rear_wheel_speed, front_wheel_angle, previous_sensor_side, side, avance)
		
		return	
		
	if obstacle_value and isObstacleCount:
		ObstacleCount =0
	
		front_wheel_angle = MIDDLE_TURN
		rear_wheel_speed = MIDDLE_SPEED
		state = "middle"
		side = "left"
		avance = true
		handle_obstacle_avoidance(delta, rear_wheel_speed, front_wheel_angle, previous_sensor_side, side, avance)
		
		return	
	"""	
	if(current_state == States.Line_Following)	:
		follow_line(delta,sensor_state,1)
		
	if current_state == States.Three_point_turn:
		advance2(delta,0,"other","none","none")
	
	
func follow_line(delta,sensor_state,speed_multiplier):
	match sensor_state:
			[false, false, true, false, false]:
				front_wheel_angle = 0.0
				rear_wheel_speed = speed_multiplier * FORWARD_SPEED
				state = "straight"
				side = "straight"
				avance = true
			[false, true, true, false, false]:
				front_wheel_angle = SLIGHT_TURN
				rear_wheel_speed = speed_multiplier * SLIGHT_SPEED
				state = "slight"
				side = "right"
				avance = true
			[false, true, false, false, false]:
				front_wheel_angle = MIDDLE_TURN
				rear_wheel_speed = speed_multiplier * MIDDLE_SPEED
				state = "middle"
				side = "right"
				avance = true
			[true, false, false, false, false], [true, true, false, false, false]:
				front_wheel_angle = STRONG_TURN
				rear_wheel_speed = speed_multiplier * STRONG_SPEED
				state = "strong"
				side = "right"
				avance = true
			[true, true, true, false, false], [true, true, true, true, false]:
				front_wheel_angle = EXTREME_TURN
				rear_wheel_speed = speed_multiplier * EXTREME_SPEED
				state = "extremeLeft"
				side = "right"
				avance = true
			[false, false, true, true, false]:
				front_wheel_angle = SLIGHT_TURN
				rear_wheel_speed = speed_multiplier * SLIGHT_SPEED
				state = "slight"
				side = "left"
				avance = true
			[false, false, false, true, false]:
				front_wheel_angle = MIDDLE_TURN
				rear_wheel_speed = speed_multiplier * MIDDLE_SPEED
				state = "middle"
				side = "left"
				avance = true
			[false, false, false, false, true], [false, false, false, true, true]:
				front_wheel_angle = STRONG_TURN
				rear_wheel_speed = speed_multiplier * STRONG_SPEED
				state = "strong"
				side = "left"
				avance = true
			[false, true, true, true, true], [false, false, true, true, true]:
				front_wheel_angle = EXTREME_TURN
				rear_wheel_speed = speed_multiplier * EXTREME_SPEED
				state = "extremeRight"
				side = "left"
				avance = true
			[false, true, true, true, false]:
				front_wheel_angle = EXTREME_TURN
				rear_wheel_speed = 0
				state = "extremeRight"
				side = "left"
				avance = true
			[false, false, false, false, false]:
				front_wheel_angle = 0
				rear_wheel_speed = 0
				state = "none"
				side = "none"
				avance = true
				off_track_count += 1
				#if off_track_count > MAX_OFF_TRACK_COUNT:
					#reverse_and_correct(delta, rear_wheel_speed, front_wheel_angle, state, side)
					#off_track_count = 0
				#return
			_:
				off_track_count = 0
				front_wheel_angle = 0
				rear_wheel_speed = 0
				state = "other"
				
	advance2(delta, rear_wheel_speed, state, side, sensor_state)

	
func change_state(Is_colliding):
	
	if  current_state == States.Obstacle_Avoidance:
		current_state = States.Obstacle_Avoidance

	elif current_state != States.Obstacle_Avoidance and Is_colliding:
		current_state = States.Obstacle_Avoidance
	else:
		current_state = States.Line_Following

func advance2(delta, speed, _state, _side, _sensor_state):
	
	var angle = deg_to_rad(front_wheel_angle)
	if _side == "left" and _state != "extremeLeft" and _state != "extremeRight":
		rotation(delta, speed, angle, previous_sensor_side, _side, avance)
		
	if _side == "right" and _state != "extremeLeft" and _state != "extremeRight":
		rotation(delta, speed, angle, previous_sensor_side, _side, avance)
		
	if state == "extremeLeft" :
		rotation(delta, speed, angle, previous_sensor_side, _side, avance)
		
	if state == "extremeRight":
		rotation(delta, speed, angle, previous_sensor_side, _side, avance)
	
	else:
		rotation(delta, speed, angle, previous_sensor_side, _side, avance)

	previous_sensor_side = _side


func handle_obstacle_avoidance(delta, _speed, _angle, _previous_sensor_side, _side, _avance):
	
	_angle = deg_to_rad(_angle)

	if 	ObstacleCount < 50:
		ObstacleCount += 1
		rotation(delta, _speed, _angle, _previous_sensor_side, _side, _avance)
	if 	ObstacleCount == 50:
	
		ObstacleCount = 0
		isObstacleCount = false
			

func rotation(delta, _speed, _angle, _previous_sensor_side, _side, _avance):
	var direction = Vector3.ZERO
	var direction_x = Vector3.ZERO
	var direction_z = Vector3.ZERO

	if(_previous_sensor_side == ""):
		
				
		direction_z = global_transform.basis.z.normalized()
		direction = (direction_z).normalized()
		translate(direction * _speed * delta)
		_previous_sensor_side  == "straight"
		previousDirection = direction
		previousDirectionX = direction[0]
		previousDirectionZ = direction[2]
		return
	
	if _angle != 0  :
		if (_side == "left"):
			_angle = (-_angle)
			
		rotate_y(_angle * delta)

	if _avance:
		
		if _previous_sensor_side == _side:
				direction = previousDirection
		else:
			if(_side == "straight"):
				if previousDirectionZ>0:
					previousDirectionZ = previousDirectionZ
					previousDirection[2] = previousDirectionZ
				direction = previousDirection
			
			else:
		
				#if previousDirectionX == 0 and _side == "right":
					#previousDirectionX = (-1)*previousDirectionX
				if previousDirectionZ>0:
					previousDirectionZ =previousDirectionZ
					previousDirection[3] = previousDirectionZ
			
				
				direction = previousDirection
		
		translate(direction * _speed * delta)
		previousDirectionX = direction[0]
		previousDirectionZ = direction[2]
		previousDirection = direction 
