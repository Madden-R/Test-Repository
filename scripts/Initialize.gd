extends Node2D
class_name Swarm_Sim

@export_group("Obstacle Generation")
@export_enum("triangle", "rectangle") var obstacle_shape := "triangle"  ## Shape of the obstacle field, either 'triangle' or 'rectangle'
@export var obstacle_width := 4  ## Number of obstacles along the y-axis of the field. If triangular, the width of the base
@export var obstacle_depth := 4  ## Number of obstacles along the x-axis of the field. If triangular, this is ignored
@export var obstacle_spacing := 60  ## Spacing in pixels between obstacles
#@export_range(0, 100, 1, "suffix:%") var obstacle_randomization: float  ## Maximum randomization offset, where 100% is the maximum range between obstacles without collisions
@export var obstacle_randomization := 50
@export var obstacle_scale := 1.0  ## Scale of the obstacle image and collision circle

@export_group("Drone Properties")
@export_enum("Centralized", "Decentralized") var control: String = "Decentralized" ## right now used for logging.
@export var droneNum: int ## Number of drones to generate
@export var weighted_direction: bool

@export_range(1, 180, 1, "suffix:°") var Maximum_Angle: float

@onready var start: Area2D = $Start
@onready var end: Area2D = $End
@onready var obstacles: Node2D = $Obstacles_Group
@onready var drones: Node2D = $Drones_Group
@onready var logger: DataLogger = $logger

@export_group("Logging")
@export var timer_wait_time_ms: int ## how often (in milliseconds) to capture drones' motionpath data.
@export var log_delay_sec: int
@export var id_number: int 
# NOTE: The logger's experiment_type variable must be set during this script's _ready() function to avoid error.
var experiment_type: String ## Used for setting the filepath in the logger.

const OBSTACLE_SIZE = 32  ## size in pixels of the obstacle image

# Optionally initialize the board.
func _ready() -> void:
	
	# make sure the logger is configured properly. The logger's id_number is set in the SimulationRunner script.
	logger.drones = drones
	logger.simulator = self
	logger.strategy = control
	logger.maxAngle = Maximum_Angle
	logger.experiment_type = experiment_type
	logger.id_number = id_number
	logger.init_timer(timer_wait_time_ms, log_delay_sec) # initialize the timer to gather data from the drones.
	logger.init_filepath()
	
	Maximum_Angle = deg_to_rad(Maximum_Angle)
	var start_point = obstacles.position + Vector2(140, 0)
	if obstacle_shape == "triangle":
		generate_triangle(start_point)
	else:
		generate_rectangle(start_point)
	
	create_drones()
	
	print ("simulation " + str(id_number) + " is up & running!")

## gets a reference to the logger node.
func get_logger():
	return logger

## gets a reference to the drones.
func get_drones():
	return drones

## gets a reference to the obstacles.
func get_obstacles():
	return obstacles

## Initialize drones in start region based on the parameters.
func create_drones():
	var drone = preload("res://scenes/plinko_drone.tscn")
	for i in range(droneNum):
		var newDrone = drone.instantiate()

		# changed to romove "drone_" from the name. This will make it easier to log data.
		newDrone.name = str(i) 
		newDrone.move_speed = 80

		var start_offset = Vector2(-start.get_child(0).shape.radius, 0)
		var end_offset = Vector2(end.get_child(0).shape.size.x/2.0, 0)
		newDrone.start_point = start.global_position + start_offset
		newDrone.end_point = end.global_position

		newDrone.max_angle = Maximum_Angle
		newDrone.weighted = weighted_direction

		var randOffset = Vector2(randf() * 50 - 25, randf() * 50 - 25)
		newDrone.position = start.position + randOffset

		drones.add_child(newDrone)
		# print("Drone sprite texture:", newDrone.get_node("Sprite2D").texture)
		# print("Drone position", newDrone.position)

## Generates obstacles in a triangular plinko formation
func generate_triangle(start_point: Vector2) -> void:
	# print("Generating obstacles in a triangular plinko formation")

	var obstacle = preload("res://scenes/obstacle.tscn")
	for row in obstacle_width:
		for col in row + 1:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", row, col)

			new_obstacle.position.x = start_point.x + (row * obstacle_spacing)
			new_obstacle.position.y = start_point.y + (col * obstacle_spacing) - (row * obstacle_spacing / 2.0)
			new_obstacle.apply_scale(Vector2(obstacle_scale, obstacle_scale))

			new_obstacle.position += randomize_position()

			obstacles.add_child(new_obstacle)

## Generates obstacles in a rectangular plinko formation
## The start vector corresponds to the middle of the first row of obstacles
func generate_rectangle(start_point: Vector2) -> void:
	# print("Generating obstacles in a rectangular formation")

	var obstacle = preload("res://scenes/obstacle.tscn")
	for row in obstacle_depth:
		var width = obstacle_width
		if (row % 2):
			width -= 1

		for col in width:
			var new_obstacle = obstacle.instantiate()
			new_obstacle.name = str("obstacle_", row, col)

			new_obstacle.position.x = start_point.x + (row * obstacle_spacing)
			new_obstacle.position.y = start_point.y + (col * obstacle_spacing) - (width * obstacle_spacing) / 2.0 + (obstacle_spacing / 2.0)
			new_obstacle.apply_scale(Vector2(obstacle_scale, obstacle_scale))
			new_obstacle.position += randomize_position()

			obstacles.add_child(new_obstacle)


## Returns the randomization offset vector, accounting for max spacing.
func randomize_position() -> Vector2:
	var max_rand_offset = ((obstacle_spacing / 2.0) - (obstacle_scale * OBSTACLE_SIZE) / 2.0) * (obstacle_randomization / 100.0)
	var rand_vector = Vector2(max_rand_offset * randf_range(-1, 1), max_rand_offset * randf_range(-1, 1))
	return rand_vector

func _draw() -> void:
	var endpoint = Vector2(-cos(Maximum_Angle), sin(Maximum_Angle)) * 400
	draw_line(end.global_position, end.global_position + endpoint, "red", 3)
	draw_line(end.global_position, end.global_position + endpoint * Vector2(1, -1), "red", 3)
