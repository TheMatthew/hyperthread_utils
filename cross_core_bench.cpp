#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <atomic>
#ifdef _WIN32
#include <windows.h>
#else
#include <pthread.h>
#include <sched.h>
#endif

// Set CPU affinity for the current thread
void setThreadAffinity(int cpu) {
#ifdef _WIN32
    DWORD_PTR mask = (1ULL << cpu);
    SetThreadAffinityMask(GetCurrentThread(), mask);
#else
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
#endif
}

// Perform a heavy arithmetic workload
void arithmeticBenchmark(std::atomic<bool>& ready, std::atomic<bool>& stop, int cpu, long long& result) {
    setThreadAffinity(cpu);
    long long sum = 0;
    while (!ready.load())
        ; // Wait for the start signal

    while (!stop.load()) {
        for (int i = 0; i < 1000; ++i) {
            sum += i * 2;  // Multiplication and addition
        }
    }

    result = sum;
}

// Measure the bandwidth of running arithmetic operations on two cores simultaneously
double measureBandwidth(int cpu1, int cpu2) {
    std::atomic<bool> ready(false);
    std::atomic<bool> stop(false);
    long long result1 = 0, result2 = 0;

    // Launch two threads, one on each CPU
    std::thread t1(arithmeticBenchmark, std::ref(ready), std::ref(stop), cpu1, std::ref(result1));
    std::thread t2(arithmeticBenchmark, std::ref(ready), std::ref(stop), cpu2, std::ref(result2));

    // Synchronize threads
    ready.store(true);
    auto start = std::chrono::high_resolution_clock::now();

    // Let the threads run for a short duration
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    auto end = std::chrono::high_resolution_clock::now();
    stop.store(true);

    t1.join();
    t2.join();

    // Calculate bandwidth (operations per second)
    auto elapsed = std::chrono::duration<double>(end - start).count();
    return (result1 + result2) / elapsed / 1e6; // Bandwidth in MegaOps/second
}

int main() {
    const int num_cpus = std::thread::hardware_concurrency();
    std::cout << "Number of CPUs: " << num_cpus << std::endl;

    // Open CSV file for writing
    std::ofstream csvFile("core_bandwidth.csv");
    if (!csvFile.is_open()) {
        std::cerr << "Failed to open CSV file for writing!" << std::endl;
        return 1;
    }

    // Write CSV headers
    csvFile << "CPU";
    for (int cpu2 = 0; cpu2 < num_cpus; ++cpu2) {
        csvFile << "," << cpu2;
    }
    csvFile << "\n";

    // Measure bandwidths and write to CSV
    for (int cpu1 = 0; cpu1 < num_cpus; ++cpu1) {
        csvFile << cpu1; // Row label
        for (int cpu2 = 0; cpu2 < num_cpus; ++cpu2) {
            if (cpu1 == cpu2) {
                csvFile << ",0"; // Bandwidth to itself is meaningless
            } else {
                double bandwidth = measureBandwidth(cpu1, cpu2);
                csvFile << "," << std::fixed << std::setprecision(2) << bandwidth;
            }
        }
        csvFile << "\n";
    }

    csvFile.close();
    std::cout << "Bandwidth results written to core_bandwidth.csv" << std::endl;

    return 0;
}

