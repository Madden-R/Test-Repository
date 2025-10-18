# PLINKO DRONES

A simulation of drones in a plinko environment with rudimentary object avoidance.
Open this file folder in GODOT.
This project was most recently edited in godot 4.5 but should not cause issues with earlier versions of the engine.

## The Simulator:

The simulator runs the simulation & can be used to configure parameters, using the inspector panel.

### IMPORTANT:

The simulations are designed to be run by the SimulationRunner, so it is not a good idea to run the simulations yourself.
Use the methods defined in the SimulationRunner script instead.

## Simulation Runner:

A script able to run multiple simulations at once. It has methods listed below:

- create_sim() which returns a simulation node configured by the parameters passed as arguments.
- create_sim_from_array() which does the same as above but takes an array of parameters as arguments. (PREFERRED USAGE)
- add_sim() which takes a simulation node as an argument & adds it to the tree, staring its process loop.

### Usage:

The SimulationRunner is meant to be used on its own. That means to run it as the main scene.
create_sim() and create_sim_from_array() create & configure a simulation for use, but it cannot be run until added to the tree, which add_sim() is responsible for.
Sample usage is provided in the node's _ready() function, found in `SimulationRunner.gd`

## The Drones:

The drones move forward at a customizeable speed.
When encountering an obstacle, they move either left or right with a customizeable probability.
Drones switch direction if about to collide with an obstacle from the side.
Drones no longer collide with each other.

Drones can also be configured to weight their probability using the angle to the goal location.
Drone count & directional weighting is configured via the SimulationRunner script.

NOTE: like real life plinko, drones can get stuck.

## The Logger:

Logs motionplan (spatial) & makespan data to the correct filepaths.
File system MUST be configured per specifications in the Structure section of this README. fileSystem-guide.png in the assets folder for reference.
If I (Madden) uploaded everything correctly, The logger file should be properly configured with the other files.

## Headless Usage




Linux: run a single simulation without visualization with the following command:

```bash
godot --headless --script scripts/run_sim_headless.gd -- [USER ARGS]
```

(In theory this should work on WSL, but doesn't)

## Analysis

The `analytics` folder contains scripts and tools for analyzing and visualizing the results of drone navigation experiments. These scripts process the data collected by the logger to provide detailed statistical and graphical comparisons of different navigation strategies.

### Analysis Scripts

- **`analytics.py`**
  - Main entry point for all analysis and visualization tasks.
  - Reads experiment data from the `sampleOutput` directory (or any compatible data folder).
  - Computes descriptive statistics (count, mean, std, min, 25%, median, 75%, max) for each group (e.g., strategy) and prints them to the CLI for every plot.
  - Generates boxplots for bothFixed experiments, showing the full distribution of makespan, traversal time, and Wasserstein EMD (Earth Mover's Distance) for each strategy.
  - Generates scatter plots with linear best-fit lines for angleFixed and countFixed experiments, visualizing trends across drone count or angle.
  - Handles missing or malformed data robustly, with clear warnings and error handling.
  - Modular and extensible: all major analysis and plotting logic is broken into reusable, well-documented functions.
  - Designed for reproducibility: all results and statistics are printed and visualized for transparency.

- **`generateFakeData.py`**
  - Utility script for generating realistic, trending, headerless fake data files for both makespan and spatial experiments.
  - Automatically creates the required directory structure and populates it with data files for both centralized and decentralized strategies.
  - Ensures that centralized data is always "better" (lower makespan/traversal/EMD) than decentralized, for clear comparison.
  - Supports both makespan and spatial experiment types, with data that varies by drone count and angle.
  - Useful for testing the analysis pipeline, demos, or development without running full simulations.

### Example Data: `sampleOutput/`

The `sampleOutput/` directory contains example output data files and directory structure for makespan and spatial experiments, including both centralized and decentralized strategies. This folder is structured to match the expected input for the analysis scripts.

- **Structure:**
  - `output-data/` is a subfolder of `res://` & contains two main subfolders:
	- `initialTestFiles/`: Contains simple, small-scale or example data files for quick testing and validation of the analysis pipeline. These files are useful for verifying script functionality and for demonstration purposes. File names and contents are minimal and may not cover all experiment types.
	- `root/`: The main data directory used for full analysis. This folder is structured as follows:
	  - `Makespan/` and `Spatial/` directories, each representing a different type of experiment data (makespan or spatial/motionpath).
		- Each of these contains subfolders for `Centralized/` and `Decentralized/` strategies.
		  - Within each strategy folder, there are further subfolders for each experiment type:
			- `BothFixed/`: Contains data files where both drone count and angle are fixed.
			- `AngleFixed/`: Contains data files where the angle is fixed and drone count varies.
			- `CountFixed/`: Contains data files where the drone count is fixed and angle varies.
		  - Each experiment subfolder contains one or more `.txt` data files, each representing a single experiment run or configuration. These files are headerless and formatted for direct use with the analysis script.
  - All data files are structured for compatibility with the analysis pipeline and are organized to allow easy comparison between strategies and experiment types.

### Usage

1. **Run Experiments:** Use the simulator and logger to generate entry/exit and motionpath data files, or use `generateFakeData.py` to create test data in the correct structure. Ensure that your makespan and spatial data files are headerless and formatted correctly, with values separated by commas. Refer to the `sampleOutput/` directory for examples of the expected structure.
2. **Analyze Data:** Run `analytics.py` to process the data, compute statistics, and generate plots. All results and statistics are printed to the CLI and shown as visualizations. Before running, ensure the configurable constants in `analytics.py` are set correctly:
   - **`ROOT_FOLDER`**: Path to the root directory containing experiment data.
   - **`MAKESPAN_DIR`**: Subdirectory name for makespan experiment data.
   - **`SPATIAL_DIR`**: Subdirectory name for spatial experiment data.
   - **`STRATEGIES`**: List of strategies to analyze (e.g., `['centralized', 'decentralized']`).
   - **`FOLDER_TYPES`**: Types of experiments (e.g., `['bothFixed', 'angleFixed', 'countFixed']`).
   - **`PLOT_COLORS`**: Colors for different plot elements:
	 - `[0]`: Data points in scatter plots, box color in boxplots.
	 - `[1]`: Best-fit line in scatter plots, median line in boxplots.
	 - `[2]`: Whiskers and caps in boxplots.
	 - `[3]`: Outlier (flier) points in boxplots.
   - **`FIGURE_SIZE`**: Dimensions of the generated plots (width, height).
   - **`BOX_WIDTH`**: Width of boxplots.
   - **`FONT_SIZE`**: Font size for plot titles and labels.
   - **`BEST_FIT_DEGREE`**: Degree of the best-fit line for scatter plots (e.g., `1` for linear).
   - **`BEST_FIT_LABEL`**: Labels for best-fit lines based on degree (e.g., `Linear Best Fit`, `Quadratic Best Fit`).
   - **`CONFIDENCE_LEVEL`**: Confidence level for margin of error calculations (e.g., `0.95`).
   - **`SHOW_MEANS`**: Whether to show means in boxplots.
   - **`SHOW_LEGEND`**: Whether to display legends in plots.
3. **Interpret Results:** Use the generated plots and printed statistics to compare navigation strategies, understand performance trends, and identify areas for improvement. For example:
   - Boxplots show the distribution of makespan, traversal time, and Wasserstein EMD for each strategy.
   - Scatter plots visualize trends across drone count or angle, with best-fit lines for clarity.

For more details, see the docstrings and comments within each script. All code is modular, robust, and designed for easy extension and reproducibility.
