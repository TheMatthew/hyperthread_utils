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

// Measure communication latency between two threads
double measureLatency(int cpu1, int cpu2) {
    if (cpu1 == cpu2)
	return 0.0;
    std::atomic<bool> ready(false);
    std::atomic<bool> signal(false);
    // Worker thread
    auto worker = [&](int cpu) {
        setThreadAffinity(cpu);
        while (!ready.load())
            ; // Wait for readiness signal
        for (int i = 0; i < 1000000; ++i) {
            signal.store(true);
            while (signal.load())
                ; // Wait for main thread
        }
    };

    // Bind worker thread to CPU1
    std::thread t(worker, cpu1);

    // Bind main thread to CPU2 and synchronize
    setThreadAffinity(cpu2);
    ready.store(true);

    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < 1000000; ++i) {
        while (!signal.load())
            ; // Wait for worker thread
        signal.store(false);
    }
    auto end = std::chrono::high_resolution_clock::now();
    t.join();

    // Calculate latency
    return std::chrono::duration<double>(end - start).count() / 1000000.0;
}

int main() {
    const int num_cpus = std::thread::hardware_concurrency();
    std::cout << "Number of CPUs: " << num_cpus << std::endl;

    // Open CSV file for writing
    std::ofstream csvFile("core_latencies.csv");
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

    // Measure latencies and write to CSV
    for (int cpu1 = 0; cpu1 < num_cpus; ++cpu1) {
        csvFile << cpu1; // Row label
        for (int cpu2 = 0; cpu2 < num_cpus; ++cpu2) {
            double latency = measureLatency(cpu1, cpu2);
            csvFile << "," << std::fixed << std::setprecision(3) << latency*1e9;
        }
        csvFile << "\n";
    }

    csvFile.close();
    std::cout << "Latencies written to core_latencies.csv" << std::endl;

    return 0;
}

