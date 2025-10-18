extends SceneTree

var scene_path := "res://scenes/field.tscn"
# var Init = preload("res://scripts/Initialize.gd").new()
var N_arg := 20
var w_arg := false

func parse_command_line_args():
	var args = OS.get_cmdline_args()
	print(args)

	for i in range(args.size()):
		match args[i]:
			"-w":
				print("weighted")
			"-N":
				if i + 1 < args.size():
					N_arg = args[i + 1].to_int()

func load_and_run_simulation(angle: float, N: int, weighted=true):
	# load base scene to godot
	var scene_res = load(scene_path)
	if not scene_res:
		push_error("Failed to load scene: " + scene_path)
		quit(1)
	var scene_instance = scene_res.instantiate()
	if not scene_instance:
		push_error("Failed to instance scene.")
		quit(1)
	root.add_child(scene_instance)
	var sim = root.get_node("Simulator")

	# DEFAULTS
	###
	sim.obstacle_width = 6
	sim.obstacle_depth = 6
	sim.log_button.emit_signal("pressed")

	# SET FOR THIS SIMRUN
	###
	sim.droneNum = N
	sim.weighted_direction = w_arg
	sim.Maximum_Angle = angle
	var w = "uw"
	if weighted:
		sim.weighted_direction = true
		w = "w"

	# SET LOGS
	###
	# set logging filename based on variable values in this sim
	var filename_base = "data-"+w+"-N"+str(sim.droneNum)+"-A"+str(int(sim.Maximum_Angle))
	var filename_ee = filename_base+"-ee"
	var filename_cont = filename_base+"-cont"
	sim.filename_ee = filename_ee # idk anymore
	sim.filename_cont = filename_cont
	var filepath_ee = "res://output-data/" + filename_ee + ".txt"
	var filepath_cont = "res://output-data/" + filename_cont + ".txt"

	# TODO figure out how to end simulation based on fraction of bots at global_position
	# Set up a timeout timer to log and quit if simulation takes too long
	var timeout_seconds = 20  # adjust as needed
	var timer = Timer.new()
	timer.wait_time = timeout_seconds
	timer.one_shot = true
	timer.autostart = true
	root.add_child(timer)
	timer.connect("timeout", func():
		print("Simulation timeout reached, logging and quitting.")
		sim.logger.log_data_ee(filepath_ee)
		sim.logger.log_data_cont(filepath_cont)
		#sim.connect("simulation_completed", Callable(sim.logger, "log_data_ee").bind(filepath_ee))
		#sim.connect("simulation_completed", Callable(sim.logger, "log_data_cont").bind(filepath_cont))
		quit()
	)

func _init():
	#parse_command_line_args() # not working, need to compile / export?

	# TODO figure out how to spawn in separate threads
	for w in [true, false]:
		for N in range(5,21,5):
			for angle in range(30, 41, 5):
				load_and_run_simulation(angle, N, w)
				#quit()
