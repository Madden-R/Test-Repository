import subprocess
import os
import time

GODOT_PATH = "cluttered-navigation/godot.exe"
PROJECT_PATH = "cluttered-navigation"
SIMULATIONS = 15
DRONE_COUNTS = range(2, 2 + SIMULATIONS)
DRONE_DATA_FILE = "cluttered-navigation/drones-data.txt"

def run_sim(drone_count, sim_id):
    print(f"Running simulation {sim_id+1}/{SIMULATIONS} with {drone_count} drones...")
    env = {**os.environ, "DRONE_COUNT": str(drone_count)}
    cmd = [GODOT_PATH, "--headless", "--path", PROJECT_PATH, "--quit", "--", f"--drone-count={drone_count}", f"--sim-id={sim_id}"]
    subprocess.run(cmd, env=env)
    time.sleep(0.5)

def main():
    if os.path.exists(DRONE_DATA_FILE):
        os.remove(DRONE_DATA_FILE)
    for i, n in enumerate(DRONE_COUNTS):
        run_sim(n, i)
    print("Done. See results in:", DRONE_DATA_FILE)

if __name__ == "__main__":
    main()
