#extends VehicleBody3D
#
## Constantes
#const FORWARD_SPEED = 1.0
#const BACKWARD_SPEED = 1.0
#const SLIGHT_TURN_LEFT = 10.0
#const SLIGHT_TURN_RIGHT = -10.0
#const MIDDLE_TURN_LEFT = 20.0
#const MIDDLE_TURN_RIGHT = -20.0
#const STRONG_TURN_LEFT = 30.0
#const STRONG_TURN_RIGHT = -30.0
#const MAX_OFF_TRACK_COUNT = 10  # Doit être positif
#const MAX_SPEED = 1.0 
#const OBSTACLE_STOP_DISTANCE = 3.0
#const RECOVERY_DISTANCE = 3.0
#
#var left_sensor: RayCast3D
#var center_sensor: RayCast3D
#var right_sensor: RayCast3D
#var center_left_sensor: RayCast3D
#var center_right_sensor: RayCast3D
#var obstacle_sensor: RayCast3D
#var avant_passager: VehicleWheel3D
#var arriere_passager: VehicleWheel3D
#var avant_conducteur: VehicleWheel3D
#var arriere_conducteur: VehicleWheel3D
#
#var front_wheel_angle = 0.0
#var rear_wheel_speed = 6.0
#var off_track_count = 0
#
## Capteurs
#var sensors = []
#
#func _ready():
#
	#
	#left_sensor = $"LeftSensor"
	#center_sensor = $"CenterSensor"
	#right_sensor = $"RightSensor"
	#center_left_sensor = $"CenterLeftSensor"
	#center_right_sensor = $"CenterRightSensor"
	#obstacle_sensor = $"Obstacle"
	#
	## Activer les capteurs
	#left_sensor.enabled = true
	#center_sensor.enabled = true
	#right_sensor.enabled = true
	#center_left_sensor.enabled = true
	#center_right_sensor.enabled = true
	#obstacle_sensor.enabled = true  # Activer le capteur d'obstacle
#
	## Activer le traitement de l'objet
	#set_process(true)
#
#func _process(delta):
	## Lire les états des capteurs
	#var left_value = left_sensor.is_colliding()
	#var center_value = center_sensor.is_colliding()
	#var right_value = right_sensor.is_colliding()
	#var center_left_value = center_left_sensor.is_colliding()
	#var center_right_value = center_right_sensor.is_colliding()
	#var obstacle_value = obstacle_sensor.is_colliding()  # État du capteur d'obstacle
	#var sensor_state = [left_value, center_left_value, center_value, center_right_value, right_value]
#
	#if obstacle_sensor.is_colliding():
		#var obstacle_distance = obstacle_sensor.get_collision_point().distance_to(global_transform.origin)
		#if obstacle_distance <= OBSTACLE_STOP_DISTANCE:
			#return  # Arrêter le véhicule
#
	## Gestion de la position du véhicule
	#var position = global_transform.origin
	#if position.y < 0.5:  
		#position.y = 0.5  
		#global_transform.origin = position
#
	#match sensor_state:
		#[false, false, true, false, false]:
			## Avancer droit
			#front_wheel_angle = 0.0
			#rear_wheel_speed = FORWARD_SPEED
			#off_track_count = 0
		#[false, true, true, false, false]:
			## Tourner légèrement à gauche
			#front_wheel_angle = SLIGHT_TURN_LEFT
			#rear_wheel_speed = FORWARD_SPEED
		#[false, true, false, false, false], [true, true, false, false, false], [true, true, true, false, false]:
			## Tourner légèrement à gauche
			#front_wheel_angle = MIDDLE_TURN_LEFT
			#rear_wheel_speed = FORWARD_SPEED
		#[true, false, false, false, false]:
			## Tourner fortement à gauche
			#front_wheel_angle = STRONG_TURN_LEFT
			#rear_wheel_speed = FORWARD_SPEED
		#[false, false, true, true, false]:
			## Tourner légèrement à droite
			#front_wheel_angle = SLIGHT_TURN_RIGHT
			#rear_wheel_speed = FORWARD_SPEED
		#[false, false, false, true, false], [false, false, false, true, true], [false, false, true, true, true]:
			## Tourner légèrement à droite
			#front_wheel_angle = STRONG_TURN_RIGHT
			#rear_wheel_speed = FORWARD_SPEED
		#[false, false, false, false, true]:
			## Tourner fortement à droite
			#front_wheel_angle = MIDDLE_TURN_RIGHT
			#rear_wheel_speed = FORWARD_SPEED
		#[false, false, false, false, false]:
			## Reculer pour se remettre sur la piste
			#off_track_count += 1
			#if off_track_count > MAX_OFF_TRACK_COUNT:
				#reverse_and_correct(delta)
				#off_track_count = 0
			#return
		#_:
			## Aucun cas particulier, réinitialiser le compteur de piste
			#off_track_count = 0
#
	## Vérifier la détection d'obstacles
	#if obstacle_value:
		#handle_obstacle_avoidance()  # Gérer l'évitement d'obstacles
#
	## Appliquer les vitesses aux roues
	#advance(rear_wheel_speed)
#
#func advance(rear_wheel_speed):
	## Appliquer la force du moteur
	#var engine_force = rear_wheel_speed * mass  # Définir la force du moteur
	#set_engine_force(engine_force)  # Ajuster la force du moteur
	  ## Ajuster la vitesse des roues arrière
	#rear_wheel_speed = engine_force / mass
	#var direction = Vector3.ZERO
	#var rotation_angle = deg_to_rad(front_wheel_angle)
	#var turn_direction = 0
#
	## Définir la direction de base en fonction de la transformation
	#direction.z = -global_transform.basis.z.z
	#
	## Définir la direction en fonction de l'angle des roues avant
	#if front_wheel_angle != 0:
		#var angular_velocity = rotation_angle # Exemple : rotation autour de l'axe Y
		#set_angular_velocity(angular_velocity)
	## Calculer la force linéaire à appliquer
	#var linear_force = direction.normalized() * engine_force
	#set_linear_velocity(linear_force.normalized() * rear_wheel_speed)
#
	## Appliquer la force linéaire
	#var gravity_force = Vector3(0, -9.81 * mass, 0)  # Appliquer une force de gravité
	#apply_central_force(gravity_force)
	#
	#var linear_velocity = direction.normalized() * rear_wheel_speed
#
	#
#
#func reverse_and_correct(delta):
	## Arrêter le mouvement avant de reculer
	## Reculer sur une distance suffisante
	#var reverse_distance = RECOVERY_DISTANCE  # Augmentez la distance de recul ici
	#rear_wheel_speed = -BACKWARD_SPEED
	#advance(rear_wheel_speed)  # Appliquer la vitesse de recul
	#
	## Attendre un court délai pour reculer
	## Vous pouvez utiliser un timer ici si besoin
#
#func handle_obstacle_avoidance():
	## Logique d'évitement d'obstacles
	#rear_wheel_speed = -BACKWARD_SPEED  # Reculer pour éviter l'obstacle
	#advance(rear_wheel_speed)  # Appliquer immédiatement la vitesse de recul
