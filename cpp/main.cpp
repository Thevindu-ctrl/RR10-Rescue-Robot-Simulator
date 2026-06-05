#include <iostream>
#include <thread>
#include <mutex>
#include <fstream>
#include <chrono>
#include <vector>
#include <atomic>
#include <random>
#include <iomanip>
#include <cmath>

using namespace std;
using namespace std::chrono;

//State Machine Definition

enum RobotState {
    FOLLOW_LINE = 0,     // Normal autonomous operation
    SEARCH_LINE = 1,     // Recovery mode when line is lost
    STOP_DANGER = 2,     // Emergency braking / Hazard detected
    MANUAL_OVERRIDE = 3  // External intervention mode
};

// GLOBAL THREAD SAFETY TOOLS
mutex robotDataMutex;           // Prevents data races between Control and Logging threads
atomic<bool> isSystemActive(true); //shutdown flag
atomic<RobotState> systemMode(FOLLOW_LINE); //thread safe state tracking

//OOP SENSOR ABSTRACTION

class BaseSensor {
protected:
    string typeID;
public:
    BaseSensor(string id) : typeID(id) {}
    virtual double poll() = 0; 
    virtual ~BaseSensor() {}
};

// Concrete implementation of a line sensor using a normal distribution to simulate real-world IR noise
class LineSensorArray : public BaseSensor {
public:
    LineSensorArray() : BaseSensor("LSA_01") {}
    double poll() override {
        static default_random_engine engine;
        static normal_distribution<double> noise(0.0, 0.3); // Simulate sensor jitter/variance
        return noise(engine); 
    }
};

// Represents the physical actuators (Motors)
class DriveTrain {
public:
    double speed = 0.0;
    void applyVelocity(double v) { speed = v; }
};

//MAIN ROBOT CLASS (RR10)
 
class RescueRobotRR10 {
private:
    double posX = 0.0, posY = 0.0; // Current spatial coordinates
    DriveTrain motors;
    LineSensorArray lineArray;

public:
    // Core Control Logic
    void updateInternalLogic() {
        lock_guard<mutex> lock(robotDataMutex); //to Secure data 
        double lineDeviation = lineArray.poll();

        // SIMULATED OBSTICLE
        if (posX >= 35.0 && posX < 75.0) {
            systemMode = STOP_DANGER; 
            motors.applyVelocity(0.12); // Slow down significantly

            if (posX >= 45.0 && posX < 65.0) {
                posY = 3.5; // Simulate a sharp swerve or detour
            } else {
                posY = 0.0; 
            }
        } 
        // SIMULATED HAZARD ZONE 
        else if (posX >= 150.0 && posX <= 180.0) {
            systemMode = STOP_DANGER;
            motors.applyVelocity(0.10);
            posY = lineDeviation * 0.1; 
        }
        // NORMAL PATH
        else {
            systemMode = FOLLOW_LINE;
            motors.applyVelocity(0.25);
            posY = lineDeviation * 0.12; 
        }

        posX += motors.speed; // Integrate velocity to update position
    }

    // Thread-safe method for the Logger to grab current position data
    void fetchTelemetry(double &x, double &y) {
        lock_guard<mutex> lock(robotDataMutex);
        x = posX; y = posY;
    }
}; 

RescueRobotRR10 robotRR10;

//REAL-TIME CONTROL TASK 
 //This thread runs at high frequency (50Hz / 20ms) and tracks its own performance.

void task_ControlLoop() {
    // Set up timing log for Performance Analysis
    const string TIMING_PATH = "C:\\Users\\acer\\RR10_Simulation\\logs\\timing_log.txt";
    ofstream timingLogger(TIMING_PATH);
    
    if (timingLogger.is_open()) {
        timingLogger << "sample_id,execution_time_us\n";
    }

    auto next_deadline = high_resolution_clock::now();
    int sampleCount = 0;

    while (isSystemActive) {
        // START TIMER
        auto start_time = high_resolution_clock::now();

        robotRR10.updateInternalLogic();

        // END TIMER
        auto end_time = high_resolution_clock::now();
        auto et = duration_cast<microseconds>(end_time - start_time).count();

        // Record timing for Jitter and WCET analysis 
        if (timingLogger.is_open()) {
            timingLogger << sampleCount++ << "," << et << "\n";
        }

        // RTOS SCHEDULING(20MS)
        next_deadline += milliseconds(20);
        
        // DEADLINE CHECK
        if (high_resolution_clock::now() > next_deadline) {
            next_deadline = high_resolution_clock::now(); 
        } else {
            this_thread::sleep_until(next_deadline); // Precise sleep to maintain 50Hz frequency
        }
    }
    
    if (timingLogger.is_open()) timingLogger.close();
}

//LOGGING TASK (10Hz / 100ms)


void task_LoggingLoop() {
    const string LOG_PATH = "C:\\Users\\acer\\RR10_Simulation\\logs\\log.txt";
    ofstream logger(LOG_PATH);
    
    if (!logger.is_open()) {
        cerr << "Critical Error: Could not create log file at: " << LOG_PATH << endl;
        return;
    }

    logger << "ts_ms,x,y,state\n";
    auto simStart = high_resolution_clock::now();

    while (isSystemActive) {
        double curX, curY;
        robotRR10.fetchTelemetry(curX, curY);
        
        auto now = high_resolution_clock::now();
        long ts = duration_cast<milliseconds>(now - simStart).count();

        // Write CSV formatted data
        logger << ts << "," << fixed << setprecision(3) 
               << curX << "," << curY << "," 
               << systemMode.load() << "\n";
        
        this_thread::sleep_for(milliseconds(100)); // Log at 10Hz to save disk space
    }
    logger.close();
}

// EVENT/INTERRUPT TASK
 
void task_HazardInterrupt() {
    while (isSystemActive) {
        this_thread::sleep_for(seconds(15)); 
        systemMode = MANUAL_OVERRIDE; // Force state change
        this_thread::sleep_for(seconds(2));  // Stay in override for 2 seconds
        systemMode = FOLLOW_LINE;     // Resume normal operation
    }
}

int main() {
    cout << "===========================================" << endl;
    cout << "   RR-10 EMBEDDED SIMULATION INITIALIZING" << endl;
    cout << "===========================================" << endl;

    // Launch all concurrent tasks
    thread t1_control(task_ControlLoop);
    thread t2_logging(task_LoggingLoop);
    thread t3_safety(task_HazardInterrupt);

    // Run the simulation for 45 seconds
    this_thread::sleep_for(seconds(45)); 
    
    cout << "\nShutting down simulation engine..." << endl;
    isSystemActive = false; // Signals all threads to finish their current loop
    
    // Join threads to ensure data is flushed and memory is cleaned up
    t1_control.join();
    t2_logging.join();
    t3_safety.detach(); // Detach the safety thread as it may be sleeping

    cout << "SUCCESS: All logs exported to /logs/ directory." << endl;
    return 0; 
}
