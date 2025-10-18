extends CharacterBody2D
class_name PlinkoDrone

# drone variables:
@export var move_speed: float = 100

# float for turning left or right. Left is 0, Right is 1
# Equal probability of either direction is 0.5
@export_range(0, 1, 0.01, "suffix:%") var avoid_probability: float

@export var start_point: Vector2
@export var end_point: Vector2

@export var max_angle: float
@export var weighted: bool
# scanners for obstacles.
# detector one monitors if the drone is about to hit an obstacle.
# detector 2 makes sure the drone won't crash into the same obstacle again after avoiding it.
# detectors 3 and 4 makes sure the drone won't crash going sideways
@onready var detector: Area2D = $detector
@onready var detector_2: Area2D = $detector2
@onready var detector_3: Area2D = $detector3
@onready var detector_4: Area2D = $detector4

# Entered time for logging purposes.
var time_entered

# basic state machine for plinko-based drone control.
enum states {
	ADVANCING,
	AVOIDING,
	REENTERING,
	FINISHED
}

# state variables. These are the core of the state machine.
var current_state
var direction

# ----------------------------------------------------- #

# state that moves the drone towards the target.
func advance(delta: float):

	# create a velocity vector to translate forward velocity
	# into x & y coordinates readable by the engine. Apply velocity.
	set_velocity(Vector2(move_speed, 0))

	# switch to avoiding if there is an obstacle.
	if obstacle_detected(detector):
		change_state_avoiding()
	if is_out_of_bounds():
		change_state_reenter_bounds()

# state that avoids detected obstacles
func avoid(delta: float):

	# switch directions if about to hit an obstacle from the side.
	if obstacle_detected(detector_3):
		direction = 1
	if obstacle_detected(detector_4):
		direction = -1

	# set velocity according to direction
	set_velocity(Vector2(0, move_speed * direction))

	# switch to advancing if moved away from the obstacle.
	if not obstacle_detected(detector_2):
		change_state_advancing()

func reenter():
	if (is_out_of_bounds()):
		var x_component = Vector2(0,0)
		var y_component = Vector2(0,0)
		if (position.x > end_point.x):
			x_component = Vector2(-1 * move_speed, 0)

		y_component += Vector2(0, 1 * move_speed)
		if (global_position.y > end_point.y):
			y_component *= -1
		set_velocity(x_component + y_component)
	else:
		change_state_advancing()

# -------------------------------------------------------------- #

# returns true if there is an object detected
# that isn't this drone.
func obstacle_detected(detector: Area2D) -> bool:
	for e in detector.get_overlapping_bodies():
		if e != self:
			return true
	return false

func is_out_of_bounds() -> bool:
	# imagine a line from the ending outwards at the angle specified.
	return angle_from_end() > max_angle

func angle_from_end() -> float:
	return angle_between(start_point, end_point, global_position)

#Angle in radians from points that make up angle ABC.
func angle_between(A, B, C) -> float:
	var v1 = (A - B).normalized()
	var v2 = (C - B).normalized()
	return acos(v1.dot(v2))


# returns 0.5 to -0.5 based on the angle of the drone to the end
func get_vertical_percent() -> float:
	var percent = angle_from_end() / (max_angle * 2)
	if (global_position.y < end_point.y):
		return percent
	else:
		return -percent


# change the state to advancing.
func change_state_advancing():
	current_state = states.ADVANCING

func change_state_reenter_bounds():
	current_state = states.REENTERING

func change_state_finished():
	current_state = states.FINISHED

# change the state to avoiding.
func change_state_avoiding():
	set_velocity(Vector2(0,0))

	var vertical_percent = 0
	if (weighted):
		vertical_percent = get_vertical_percent()
	# Set a random avoid direction based off the percent the drone exists
	# between the angled boundary from the end
	var rng = randf()
	direction = 1 if rng < (avoid_probability + vertical_percent) else -1

	current_state = states.AVOIDING

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	#ObstacleGenerator.generate_obstacles()
	current_state = states.ADVANCING

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:

	match current_state:
		states.ADVANCING:
			advance(delta)
		states.AVOIDING:
			avoid(delta)
		states.REENTERING:
			reenter()
		states.FINISHED:
			pass

	move_and_slide()
