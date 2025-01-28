import os
import csv

def read_cpu_topology():
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
    cpu_info = [k for k in sorted(cpu_info, key=lambda item: item['core_id'])]
    for entry in cpu_info:
        print(f"{entry['cpu']:<10} {entry['core_id']:<10} {entry['physical_package_id']:<20}")

    # Save to CSV
    save_to_csv(cpu_info)
    print("\nCPU topology saved to 'cpu_topology.csv'.")


if __name__ == "__main__":
    main()
