import os
import csv
import platform
import subprocess


def read_cpu_topology_linux_windows():
    base_path = "/sys/devices/system/cpu"
    cpu_info = []

    # Iterate over all CPU directories
    for cpu_dir in sorted(os.listdir(base_path)):
        if not cpu_dir.startswith("cpu") or not cpu_dir[3:].isdigit():
            continue

        cpu_path = os.path.join(base_path, cpu_dir, "topology")
        if not os.path.exists(cpu_path):
            continue

        # Read core_id and physical_package_id
        try:
            with open(os.path.join(cpu_path, "core_id")) as f:
                core_id = f.read().strip()
            with open(os.path.join(cpu_path, "physical_package_id")) as f:
                package_id = f.read().strip()
        except FileNotFoundError:
            continue

        cpu_info.append({
            "cpu": cpu_dir,
            "core_id": core_id,
            "physical_package_id": package_id,
        })

    return cpu_info


def read_cpu_topology_macos():
    cpu_info = []

    try:
        total_cpus = int(subprocess.check_output(["sysctl", "-n", "hw.ncpu"]).decode().strip())
        physical_cores = int(subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"]).decode().strip())
        packages = int(subprocess.check_output(["sysctl", "-n", "hw.packages"]).decode().strip())
        cores_per_package = physical_cores // packages if packages > 0 else physical_cores

        for cpu in range(total_cpus):
            physical_core = cpu % physical_cores
            package_id = physical_core // cores_per_package

            cpu_info.append({
                "cpu": f"cpu{cpu}",
                "core_id": str(physical_core),
                "physical_package_id": str(package_id)
            })

    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error reading CPU topology: {e}")
        return []

    return cpu_info


def read_cpu_topology():
    system = platform.system().lower()
    if system == "darwin":
        return read_cpu_topology_macos()
    else:
        return read_cpu_topology_linux_windows()


def save_to_csv(cpu_info, output_file="cpu_topology.csv"):
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["cpu", "core_id", "physical_package_id"])
        writer.writeheader()
        for entry in cpu_info:
            writer.writerow(entry)


def main():
    cpu_info = read_cpu_topology()
    if not cpu_info:
        print("No CPU topology information found.")
        return

    # Print topology info
    print(f"{'CPU':<10} {'Core ID':<10} {'Physical Package ID':<20}")
    print("-" * 40)
    cpu_info = sorted(cpu_info, key=lambda item: int(item['core_id']))
    for entry in cpu_info:
        print(f"{entry['cpu']:<10} {entry['core_id']:<10} {entry['physical_package_id']:<20}")

    # Save to CSV
    save_to_csv(cpu_info)
    print("\nCPU topology saved to 'cpu_topology.csv'.")


if __name__ == "__main__":
    main()
