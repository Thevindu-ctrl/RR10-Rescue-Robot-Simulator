import pandas as pd
import matplotlib.pyplot as plt

# Load the data

data = pd.read_csv(r"C:\Users\acer\RR10_Simulation\logs\log.txt")

time = data["ts_ms"]
x = data["x"]
y = data["y"]
state = data["state"]

#Graph 1: Position vs Time
plt.figure(figsize=(10, 6))
plt.plot(time, x, color='blue', label='Horizontal Progress (X)')
plt.xlabel("Time (ms)")
plt.ylabel("Position (x)")
plt.title("Robot Progress: X-Axis over Time")
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig("1_position_vs_time.png") # Distinct filename
plt.close()

# Graph 2: Error (Y) vs Time ---
plt.figure(figsize=(10, 6))
plt.plot(time, y, color='green', label='Lateral Offset (Y)')

# Logic to mark the Detour (based on X >= 45 in C++ code)
detour_mask = x >= 45
if detour_mask.any():
    detour_time = time[detour_mask].iloc[0]
    plt.axvline(x=detour_time, color='red', linestyle='--', label='Detour Start (X=45)')

plt.xlabel("Time (ms)")
plt.ylabel("Lateral Error (y)")
plt.title("Robot Navigation: Lateral Deviation (Y-Axis)")
plt.legend(loc='upper right') # Ensure legend is visible
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig("2_error_vs_time.png") # Distinct filename
plt.close()

#Graph 3: State vs Time ---
plt.figure(figsize=(10, 6))
# Using step plot for digital state changes
plt.step(time, state, where='post', color='purple', linewidth=2, label='System State')

# mark the State 3 
override_mask = state == 3
if override_mask.any():
    plt.axvspan(time[override_mask].min(), time[override_mask].max(), 
                color='orange', alpha=0.3, label='Manual Override Zone')

plt.ylim(-0.5, 4.5) 
plt.xlabel("Time (ms)")
plt.ylabel("State ID")
plt.title("System State Transitions (0: Follow, 2: Danger, 3: Override)")
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.3)
plt.savefig("3_state_vs_time.png") 
plt.close()

print("Three distinct graphs exported successfully: 1_position_vs_time.png, 2_error_vs_time.png, and 3_state_vs_time.png")