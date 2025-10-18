extends Node2D
class_name SimulationRunner

# Creates and runs simulations. Also handles the logging.

# filepath to the simulation we wish to run
var simulation = preload("res://scenes/field.tscn")

# offset variables to make sure the simulators don't run into each other.
# can run approx. 2.8 * 10^16 simulations before they run into each other.
var offset: int = 550 ## distance in y position of the simulators.
var current_pos: int = 0 ## position number of the furthest sim.
var sim_id_number: int = 0 ## id number used when creating simulations.

# to be used for the function 
const TRIANGLE = "triangle"
const RECTANGLE = "rectangle"

# Strategy
const CENTRALIZED = "Centralized"
const DECENTRALIZED = "Decentralized"

# experiment type:
const ANGLE_FIXED = "AngleFixed/"
const BOTH_FIXED = "BothFixed/"
const COUNT_FIXED = "CountFixed/"

# default parameters:
var default_parameters = [RECTANGLE, 6, 6, 75, 40, 1.0, DECENTRALIZED, 30, true, 60.0, BOTH_FIXED, 100, 10]

## returns a list of the currently running simulations
func get_running_simultations():
	return get_children()

## creates & returns a configured simulation.
func create_sim(obstacle_shape: String, obstacle_width: int, obstacle_depth: int, obstacle_spacing: int, obstacle_randomization: int, obstacle_scale: float, control: String, drone_num: int, weighted_direction: bool, max_angle: float, experiment_type: String, motionplan_log_frequency: int, log_delay_sec: int):
	var sim = simulation.instantiate() # create a new simulation
	
	# configures parameters
	sim.obstacle_shape = obstacle_shape
	sim.obstacle_width = obstacle_width
	sim.obstacle_depth = obstacle_depth
	sim.obstacle_spacing = obstacle_spacing
	sim.obstacle_randomization = obstacle_randomization
	sim.obstacle_scale = obstacle_scale
	sim.control = control
	sim.droneNum = drone_num
	sim.weighted_direction = weighted_direction
	sim.Maximum_Angle = max_angle
	sim.experiment_type = experiment_type
	sim.timer_wait_time_ms = motionplan_log_frequency
	sim.log_delay_sec = log_delay_sec
	sim.id_number = current_pos # set the sim number to properly generate filenames that don't overlap.
	
	return sim

## creates a sim from an array of parameters.
func create_sim_from_array(parameters):
	var p = parameters
	return create_sim(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12])

## add simulation to the field
func add_sim(sim: Swarm_Sim):
	
	sim.position.y = current_pos * offset    # configure position.
	add_child(sim)                           # add it to the tree.
	current_pos += 1

## Adds 3 running simulations to the field in order to test it.
func _ready() -> void:
	var sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	
	default_parameters = [RECTANGLE, 6, 6, 75, 40, 1.0, DECENTRALIZED, 30, true, 60.0, COUNT_FIXED, 100, 10]
	
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
	sim = create_sim_from_array(default_parameters)
	add_sim(sim)
