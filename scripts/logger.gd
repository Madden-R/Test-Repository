extends Node2D
class_name DataLogger
## A revised system for logging drone information from the simulation. Can choose between Logs motionplan & makespan data to csv files. Note, class is now called DataLogger because the newest version of godot has a built in Logger class

# export variables:
@export var simulator: Swarm_Sim ## simulator
@export var drones: Node2D       ## drone container

# Logging variables
var strategy: String             ## Centralized or Decentralized
var experiment_type: String      ## See the const variables.
var maxAngle: float

# Time:
var timer: Timer         # Spatial logging.
var time_start_msec: int # used for syncing motionplan & makespan data.
var log_timer: Timer     # on this timer's timeout(), saves currently logged data to CSV files. 

# data arrays: NOTE: According to the README, CSV files are to be headerless.
# var motionplan_data_header = ["strategy", "droneCount", "maxAngle", "droneID", "timeStamp", "x", "y"]
# var makespan_data_header = ["strategy", "droneCount", "maxAngle", "droneID", "entryTime", "exitTime"]
var motionplan_data = []
var makespan_data = []

# rectangle used for makespan logging
@onready var makespan_rect: Area2D = $Area2D

# ---------- F I L E P A T H S ----------------- #
const ROOT = "res://output-data/root/"
# data type: (NOTE: 'Motionplan' & 'Spatial' are used interchangably)
const MAKESPAN = "Makespan/"
const SPATIAL = "Spatial/"
# strategy:
const CENTRALIZED = "Centralized/"
const DECENTRALIZED = "Decentralized/"
# experiment type:
const ANGLE_FIXED = "AngleFixed/"
const BOTH_FIXED = "BothFixed/"
const COUNT_FIXED = "CountFixed/"

var id_number: int ## filename suffix used to generate unique filenames. Inherrited from the SimRunner's generation.
var filepath: String ## working filepath to which data is logged.
const FILENAME = "Simulation-" ## filename. Will end up as .../simulation-0.txt for example.

# -------- I N I T I A L I Z A T I O N --------- #

## Initialize & start the timer used for spatial logging. Connects the timeout() signal. Also calculates the offset since this simulation started from when the program was booted up.
func init_timer(timeout: int, log_delay_sec: int):
	
	# set up motionplan timer
	timer = Timer.new()
	timer.wait_time = (float(timeout) / 1000.0)
	
	# set up logging timer
	log_timer = Timer.new()
	log_timer.wait_time = log_delay_sec
	log_timer.set_one_shot(true)
	
	# add & connect timers
	add_child(timer)
	add_child(log_timer)
	timer.connect("timeout", log_motionplan_data)
	log_timer.connect("timeout", save_data_to_files)
	
	# start timers & calculate time offset.
	timer.start()
	log_timer.start()
	time_start_msec = Time.get_ticks_msec()
	
	# set the relative filepath & filename for storing data to. (relative from Makespan/ and Spatial/)

## Sets the filepath for logging. This must be its own function so it is called AFTER the logger's ready function. This function is called in the simulation's ready function, after the variables have been set.
func init_filepath():
		filepath = str(strategy + "/" + experiment_type + FILENAME + str(id_number) + ".txt") # the '/' is included in the experiment_type var

## returns a list of the drones in this simulation.
func get_drones():
	return drones.get_children()

## logs a 2d array as a .txt csv file into the specified filepath.
func save_csv_file(data, write_filepath: String):
	var file = FileAccess.open(write_filepath, FileAccess.WRITE)
	
	# read each element in the array (which will be a second array),
	# convert it to a PackedStringArray, & store it as a CSV line.
	for line in data:
		var csv_line = PackedStringArray(line)
		file.store_csv_line(csv_line)
	
	# close the file to prevent data leaks.
	file.close()

## called when the node enters the tree
func _ready() -> void:
	makespan_rect.connect("body_entered", log_entry_time)
	makespan_rect.connect("body_exited", log_makespan_data)
	

## gets the unique filepath to which data will be logged. Uses the filepath variable set in the _ready() function.
func get_filepath(data_type: String):
	return str(ROOT + data_type + filepath)

# -------------------- L O G G I N G ----------------- #

## logs the entry time to the drone when it enters the object field.
func log_entry_time(body: PlinkoDrone):
	body.time_entered = Time.get_ticks_msec() - time_start_msec # sync time with motionplan data

## grabs data from the drone's entry time & combines it with other data & stores as a csv line in the data array.
func log_makespan_data(body: PlinkoDrone):
	var log_line = [strategy, get_drones().size(), maxAngle, body.get_name(), body.time_entered, (Time.get_ticks_msec() - time_start_msec)]
	makespan_data.append(log_line)

## called every time the timer times out. Logs motionplan data into the data array.
func log_motionplan_data():
	var current_time = Time.get_ticks_msec()
	for drone in get_drones():
		var log_line = [strategy, get_drones().size(), maxAngle, drone.get_name(), (current_time - time_start_msec), drone.position.x, drone.position.y]
		motionplan_data.append(log_line)

## Takes the data gathered into the 2d arrays & saves them as CSV files into the system.
func save_data_to_files():
	save_csv_file(makespan_data, get_filepath(MAKESPAN))
	save_csv_file(motionplan_data, get_filepath(SPATIAL))
	print("simulation " + str(id_number) + " has logged data!")
