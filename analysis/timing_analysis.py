import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load timing data
df = pd.read_csv(r"C:\Users\acer\RR10_Simulation\logs\timing_log.txt")
et_us = df['execution_time_us']

#Calculate Metrics (Timing Table) 
avg_et = et_us.mean()
wcet = et_us.max()
target_period_us = 20000  # 20ms in microseconds
cpu_load = (avg_et / target_period_us) * 100

# Jitter is the variation between execution times
jitter = et_us.diff().abs().mean() 

print(f"--- Timing Analysis Results ---")
print(f"Average ET: {avg_et:.2f} us")
print(f"Worst-Case ET (WCET): {wcet:.2f} us")
print(f"Average Jitter: {jitter:.2f} us")
print(f"CPU Load: {cpu_load:.4f} %")
print(f"Deadline Misses: {len(et_us[et_us > target_period_us])}")

#Graphical Presentation
plt.figure(figsize=(10, 5))

# Plot Execution Time over samples
plt.plot(et_us, color='orange', label='Execution Time (ET)')
plt.axhline(y=avg_et, color='blue', linestyle='--', label=f'Avg ET ({avg_et:.1f}us)')
plt.axhline(y=wcet, color='red', linestyle=':', label=f'WCET ({wcet:.1f}us)')

plt.title("Real-Time Performance: Execution Time vs Samples")
plt.xlabel("Sample Number")
plt.ylabel("Time (microseconds)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("task5_performance_analysis.png")
plt.show()