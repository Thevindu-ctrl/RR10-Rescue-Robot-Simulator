#     Autonomous Rescue Robot Simulator (RR-10)

<div align="center">

  <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white" alt="C++" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Real--Time-FF6347?style=for-the-badge&logo=clock&logoColor=white" alt="Real-Time" />
  <img src="https://img.shields.io/badge/Embedded-000000?style=for-the-badge&logo=arduino&logoColor=white" alt="Embedded" />
  <img src="https://img.shields.io/badge/PyGame-2E8B57?style=for-the-badge&logo=pygame&logoColor=white" alt="PyGame" />
  <img src="https://img.shields.io/badge/Graphviz-87BF38?style=for-the-badge&logo=graphviz&logoColor=white" alt="Graphviz" />

</div>

<p align="center">
  <b>A high-fidelity software simulation demonstrating OOP design, multi-threading, and deterministic real-time scheduling for autonomous rescue robotics.</b>
</p>

---

## Contents

- [Overview](#project-overview)
- [System Architecture](#system-architecture)
  - [Class Hierarchy (OOP Design)](#class-hierarchy-oop-design)
  - [Concurrent Task Model](#concurrent-task-model)
  - [State Machine](#state-machine)
- [Performance Metrics](#performance-metrics)
- [Prerequisites](#prerequisites)
- [Build & Run Instructions](#build--run-instructions)
  - [Step 1: Configure Log Paths](#step-1-configure-log-paths)
  - [Step 2: Compile the C++ Engine](#step-2-compile-the-c-engine)
  - [Step 3: Run the Simulation](#step-3-run-the-simulation)
  - [Step 4: Visualize with Python](#step-4-visualize-with-python)
  - [Step 5: Generate Design Diagrams](#step-5-generate-design-diagrams)
- [Log File Formats](#log-file-formats)
  - [Telemetry Log (`log.txt`)](#telemetry-log-logtxt)
  - [Timing Log (`timing_log.txt`)](#timing-log-timinglogtxt)
- [Key Technical Features](#key-technical-features)
- [Configuration Notes](#configuration-notes)
- [Troubleshooting](#troubleshooting)


---

## Overview

The **RR-10 Autonomous Rescue Robot Simulator** is a single-file C++ application that simulates an embedded rescue robot navigating a track with obstacles and hazard zones. The project demonstrates:

- **Object-Oriented Programming (OOP)** with inheritance and composition
- **Multi-threaded concurrency** simulating RTOS task scheduling
- **Deterministic real-time control** with a 20 ms execution deadline
- **Thread-safe data sharing** using mutexes and atomic variables
- **Hardware-in-the-loop simulation** via sensor noise modelling and state-machine behaviour
- **Python-based telemetry visualization** using Pygame
- **Automated UML and architecture diagram generation** using Graphviz

The simulation runs for 45 seconds, during which the robot encounters an obstacle (position 35-75) requiring a detour, and a hazard zone (position 150-180) requiring cautious traversal.

---

## System Architecture

### Class Hierarchy (OOP Design)

```
+-------------------+       +-------------------+
|   <<abstract>>    |       |                   |
|    BaseSensor     |<------|  LineSensorArray  |
|-------------------|       |-------------------|
| # typeID: string  |       | + LineSensorArray()|
|-------------------|       | + poll(): double  |
| + poll() = 0      |       |-------------------|
+-------------------+         (Normal distribution
         ^                     noise simulation)
         |
    (inheritance)

+-------------------+       +-------------------+
|    DriveTrain     |       |  RescueRobotRR10  |
|-------------------|       |-------------------|
| + speed: double   |<>-----| - posX: double    |
|-------------------|  1   | - posY: double    |
| + applyVelocity() |       | - motors: DriveTrain|
+-------------------+       | - lineArray: LineSensorArray|
                            |-------------------|
                            | + updateInternalLogic()|
                            | + fetchTelemetry()|
                            +-------------------+
```

**Key Design Decisions:**

| Class | Responsibility | Design Pattern |
|-------|---------------|----------------|
| `BaseSensor` | Abstract interface for all sensor types | Abstract Base Class |
| `LineSensorArray` | Concrete sensor with Gaussian noise (`N(0, 0.3)`) | Polymorphism |
| `DriveTrain` | Motor actuator abstraction (velocity control) | Composition |
| `RescueRobotRR10` | Core robot logic, state transitions, telemetry | Facade / Controller |

### Concurrent Task Model

The simulator spawns **three concurrent threads** that mimic an RTOS task scheduler:

| Task | Function | Frequency | Priority | Purpose |
|------|----------|-----------|----------|---------|
| **Control Loop** | `task_ControlLoop()` | **50 Hz** (20 ms) | High | Real-time sensor polling, state machine updates, motor control |
| **Logging** | `task_LoggingLoop()` | **10 Hz** (100 ms) | Medium | Telemetry capture to CSV (`ts_ms,x,y,state`) |
| **Hazard Interrupt** | `task_HazardInterrupt()` | Every 15s + 2s hold | Low | Simulates external manual override event |

**Synchronisation Primitives:**
- `robotDataMutex` (`std::mutex`) — protects shared robot state between Control and Logging threads
- `isSystemActive` (`std::atomic<bool>`) — thread-safe shutdown flag
- `systemMode` (`std::atomic<RobotState>`) — lock-free state access across all threads

### State Machine

```
+-------------+     line lost      +-------------+
| FOLLOW_LINE |------------------->| SEARCH_LINE |
|   (green)   |<-------------------|   (yellow)  |
+-------------+     line found     +-------------+
       |                                    ^
       | obstacle/hazard                    |
       v                                    |
+-------------+     timer expired    +-------------+
| STOP_DANGER |----------------------| MANUAL_OVERRIDE|
|    (red)    |                      |    (blink)   |
+-------------+<---------------------+-------------+
```

| State | Value | Trigger | Robot Behaviour |
|-------|-------|---------|-----------------|
| `FOLLOW_LINE` | 0 | Normal operation | Full speed (0.25), follows line |
| `SEARCH_LINE` | 1 | Line deviation lost | Recovery mode (not triggered in this track) |
| `STOP_DANGER` | 2 | Obstacle (x: 35-75) or Hazard (x: 150-180) | Reduced speed, detour manoeuvre |
| `MANUAL_OVERRIDE` | 3 | External interrupt (every 15s) | Forced override for 2 seconds |

---

## Performance Metrics

Real timing analysis from `timing_log.txt` (2,246 samples across 45 seconds):

| Metric | Value | Assessment |
|--------|-------|------------|
| **Deadline** | 20,000 µs (20 ms) | Target (50 Hz) |
| **Mean Execution Time** | 2.45 µs | Excellent |
| **Worst-Case Execution Time (WCET)** | **1,056 µs** | **94.7% deadline margin** |
| **Minimum Execution Time** | 0 µs | Instant completion (cached) |
| **Jitter (WCET - Min)** | 1,056 µs | Low variance |
| **Standard Deviation** | 23.86 µs | Consistent performance |
| **Anomalies (> 50 µs)** | 9 samples (0.40%) | Negligible |

> **Conclusion:** The control loop consistently meets its 20 ms deadline with a **94.7% safety margin**, confirming deterministic real-time behaviour.

---



## Prerequisites

### Required

| Dependency | Version | Purpose |
|------------|---------|---------|
| **g++ (MinGW-w64)** | C++11 or later | Compile the simulation engine |
| **Windows OS** | 10/11 | Target platform (paths are Windows-format) |

### Python Tools (Optional)

| Dependency | Version | Install Command | Purpose |
|------------|---------|-----------------|---------|
| **Python** | 3.x (< 14) | [python.org](https://python.org) | Visualization & diagram scripts |
| **Pygame** | Latest | `pip install pygame` | Real-time robot GUI |
| **Graphviz** | 14.1.1+ | See below | UML/architecture diagram generation |

> **Important:** Python version must be **lower than 3.14** for Pygame compatibility.

### Installing Graphviz

1. Run `design/graphviz-install-14.1.1-win64.exe`
2. Add `C:\Program Files\Graphviz\bin` to your system `PATH`
3. Or uncomment the forced path line in `design_diagrams.py`:
   ```python
   os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'
   ```

---

## Build & Run Instructions

### Step 1: Configure Log Paths

**Before compiling, update the hardcoded paths** in `main.cpp` to match your system:

```cpp
// Line ~113 — Timing log path
const string TIMING_PATH = "C:\\Users\\YOUR_NAME\\RR10_Simulation\\logs\\timing_log.txt";

// Line ~156 — Telemetry log path
const string LOG_PATH = "C:\\Users\\YOUR_NAME\\RR10_Simulation\\logs\\log.txt";
```

Also update `visualize.py` (line 6):
```python
LOG_FILE = r"C:\Users\YOUR_NAME\RR10_Simulation\logs\log.txt"
```

### Step 2: Compile the C++ Engine

```bash
cd cpp
g++ -std=c++11 -O2 -pthread main.cpp -o simulate.exe
```

Flags explained:
- `-std=c++11` — Enables `<chrono>`, `<thread>`, `<mutex>`, `<atomic>`
- `-O2` — Optimisation level 2 for release performance
- `-pthread` — POSIX threading support

> **Note:** The `.dll` files in the `cpp/` folder are precompiled Windows libraries used as a g++ path bypass. They are not required if g++ is correctly added to your system PATH.

### Step 3: Run the Simulation

```bash
cd cpp
simulate.exe
```

Expected console output:
```text
===========================================
   RR-10 EMBEDDED SIMULATION INITIALIZING
===========================================

Shutting down simulation engine...
SUCCESS: All logs exported to /logs/ directory.
```

The simulation runs for **45 seconds**. Two CSV files are generated in the `logs/` folder.

### Step 4: Visualize with Python

After the simulation completes:

```bash
cd python_gui
python visualize.py
```

A Pygame window will open showing:
- **Green circle** — Robot in normal line-following mode
- **Blinking red/yellow** — Robot in obstacle avoidance zone (x: 35-75)
- **Solid red** — Robot in hazard zone (x: 150-180)
- **Live dashboard** — X/Y coordinates, current mode, action description
- **Track overlay** — Navigation line, obstacle block, hazard zone boundary

### Step 5: Generate Design Diagrams

```bash
cd design
python design_diagrams.py
```

Generates two PNG files:
- `uml_class_diagram.png` — OOP class hierarchy with inheritance/composition
- `architecture_diagram.png` — C++ Engine > CSV Logs > Python Visualizer data flow

---

## Log File Formats

### Telemetry Log (`log.txt`)

Generated at **10 Hz** by the Logging thread. Format: `CSV`

```csv
ts_ms,x,y,state
0,0.000,0.000,0
100,1.250,0.001,0
...
```

| Column | Unit | Description |
|--------|------|-------------|
| `ts_ms` | milliseconds | Elapsed simulation time |
| `x` | units | Longitudinal position along track |
| `y` | units | Lateral deviation from centre line |
| `state` | enum | Current robot state (0-3) |

**Sample Statistics (from reference run):**
- Simulation duration: **45.0 seconds**
- Total distance: **472.3 units**
- Average speed: **10.50 units/sec**
- Max Y deviation: **3.500 units** (during obstacle detour)
- State distribution: 71.7% `FOLLOW_LINE`, 28.3% `STOP_DANGER`

### Timing Log (`timing_log.txt`)

Generated at **50 Hz** by the Control thread. Format: `CSV`

```csv
sample_id,execution_time_us
0,20
1,0
2,2
...
```

| Column | Unit | Description |
|--------|------|-------------|
| `sample_id` | integer | Sequential cycle counter |
| `execution_time_us` | microseconds | Time to complete one control loop iteration |

Used for: WCET analysis, jitter measurement, deadline miss detection.

---

## Key Technical Features

| Feature | Implementation Detail |
|---------|----------------------|
| **Deterministic Scheduling** | `std::this_thread::sleep_until()` enforces rigid 20 ms cycle timing |
| **Sensor Noise Simulation** | `std::normal_distribution<double>(0.0, 0.3)` models real-world IR sensor jitter |
| **Thread Safety** | `std::lock_guard<std::mutex>` RAII pattern prevents data races |
| **State Machine** | `enum` + `std::atomic` for lock-free, interrupt-safe mode transitions |
| **WCET Logging** | Every control loop execution time is recorded for offline analysis |
| **Graceful Shutdown** | Atomic flag signals all threads; `join()` ensures data flush |
| **CSV Data Bridge** | Plain-text logs enable cross-language Python/C++ interoperability |

---

## Configuration Notes

1. **Hardcoded Paths:** All file I/O paths in `main.cpp` and `visualize.py` are absolute Windows paths. These **must** be updated before running on a different machine.

2. **g++ PATH Issue:** If `g++` is not recognised, either:
   - Add MinGW `bin/` directory to your system `PATH`, or
   - Use the provided `.dll` files in the `cpp/` folder as a runtime bypass

3. **Python Version:** Pygame is incompatible with Python 3.14+. Use Python 3.10-3.13 for best compatibility.

4. **Simulation Duration:** The 45-second runtime is defined in `main()`:
   ```cpp
   this_thread::sleep_for(seconds(45));
   ```
   Adjust this value to shorten or extend the simulation.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `simulate.exe` not found | Compilation failed | Verify g++ is installed: `g++ --version` |
| Log files not created | Path doesn't exist | Create the `logs/` directory manually |
| `pygame` import error | Pygame not installed | Run `pip install pygame` |
| Black screen in visualizer | `log.txt` path wrong | Update `LOG_FILE` path in `visualize.py` |
| Graphviz error in diagrams | Graphviz not in PATH | Install Graphviz and restart terminal |
| "Run C++ code first" message | `log.txt` missing or empty | Run the simulation before visualization |

---
