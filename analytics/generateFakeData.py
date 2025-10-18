import os
import random
import math

# Configuration for experiment structure
top_dir = os.path.join(os.path.dirname(__file__), "sampleOutput", "root")
strategies = ["centralized", "decentralized"]
experiment_types = ["makespan", "spatial"]
folders = ["angleFixed", "countFixed", "bothFixed"]
angle_range = list(range(30, 51))  # 30 to 50 inclusive
count_range = list(range(1, 21))   # 1 to 20 inclusive
mid_angle = 40.0
mid_count = 10

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def make_makespan_file(path, strategy, count, angle, fixed_type):
    # 6 columns, one line per drone
    lines = []
    for drone in range(count):
        # Centralized is always better (lower makespan)
        base = 10 + (count * 0.5) + (0 if strategy == "centralized" else 5)
        # Entry time: around 1s (in ms), exit time: 10-15s (in ms)
        entry_time = int(1000 + random.uniform(-100, 100))
        exit_time = int(random.uniform(10000, 15000))
        makespan = base + random.uniform(-1, 1)
        lines.append(f"{strategy}Weighted,{count},{angle},100{drone+1},{drone},{entry_time},{exit_time}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

def make_spatial_file(path, strategy, count, angle, fixed_type):
    # 7 columns, one line per drone per second (10 seconds)
    lines = []
    angle_rad = math.radians(angle)
    for t in range(10):
        for drone in range(count):
            # Spread drones in a fan based on angle and count
            if count > 1:
                theta = (-angle_rad/2) + (angle_rad * drone / (count-1))
            else:
                theta = 0
            # Centralized: tighter, Decentralized: more dispersed
            base_radius = 1.0 + 0.1 * t
            radius = base_radius + (0 if strategy == "centralized" else 0.2 * drone)
            x = radius * math.cos(theta) + (0 if strategy == "centralized" else 0.2)
            y = radius * math.sin(theta) + (0 if strategy == "centralized" else 0.2)
            # Add some random noise for realism
            x += random.uniform(-0.05, 0.05)
            y += random.uniform(-0.05, 0.05)
            lines.append(f"{strategy}Weighted,{count},{angle},100{drone+1},{t},{x:.2f},{y:.2f}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

def main():
    for exp_type in experiment_types:
        for strategy in strategies:
            for folder in folders:
                folder_path = os.path.join(top_dir, exp_type, strategy, folder)
                ensure_dir(folder_path)
                if folder == "angleFixed":
                    for count in count_range:
                        path = os.path.join(folder_path, f"count{count}.txt")
                        if exp_type == "makespan":
                            make_makespan_file(path, strategy, count, mid_angle, folder)
                        else:
                            make_spatial_file(path, strategy, count, mid_angle, folder)
                elif folder == "countFixed":
                    for angle in angle_range:
                        path = os.path.join(folder_path, f"angle{angle}.txt")
                        if exp_type == "makespan":
                            make_makespan_file(path, strategy, mid_count, float(angle), folder)
                        else:
                            make_spatial_file(path, strategy, mid_count, float(angle), folder)
                elif folder == "bothFixed":
                    path = os.path.join(folder_path, "fixed.txt")
                    if exp_type == "makespan":
                        make_makespan_file(path, strategy, mid_count, mid_angle, folder)
                    else:
                        make_spatial_file(path, strategy, mid_count, mid_angle, folder)

if __name__ == "__main__":
    main()
