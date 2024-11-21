## This code is coped from - https://syftbox-documentation.openmined.org/cpu-tracker-1

import os
from pathlib import Path
import json
from syftbox.lib import Client, SyftPermission
import diffprivlib.tools as dp
import time
import psutil
from statistics import mean as mn
from datetime import datetime, UTC
from typing import List

def get_cpu_usage_samples() -> List[float]:
    cpu_usage_values = []

    # Collect 50 CPU usage samples with a 0.1-second interval between each sample
    while len(cpu_usage_values) < 50:
        cpu_usage = psutil.cpu_percent()
        cpu_usage_values.append(cpu_usage)
        time.sleep(0.1)

    return cpu_usage_values

def create_restricted_public_folder(cpu_tracker_path: Path) -> None:
    os.makedirs(cpu_tracker_path, exist_ok=True)

    # Set default permissions for the created folder
    permissions = SyftPermission.datasite_default(email=client.email)
    permissions.read.append("aggregator@openmined.org")
    permissions.save(cpu_tracker_path)

def create_private_folder(path: Path) -> Path:
    cpu_tracker_path: Path = path / "private" / "cpu_tracker"
    os.makedirs(cpu_tracker_path, exist_ok=True)

    # Set default permissions for the created folder
    permissions = SyftPermission.datasite_default(email=client.email)
    permissions.save(cpu_tracker_path)

    return cpu_tracker_path


def save(path: str, cpu_usage: float) -> None:
    current_time = datetime.now(UTC)
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as json_file:
        json.dump(
            {"cpu": cpu_usage, "timestamp": timestamp_str},
            json_file,
            indent=4,
        )


def main():
    # client = Client.load()

    # Create an output file with proper read permissions
    restricted_public_folder = client.api_data("cpu_tracker")
    create_restricted_public_folder(restricted_public_folder)

    # Create private private folder
    private_folder = create_private_folder(client.datasite_path)

    # Get cpu usage mean with differential privacy in it.
    cpu_usage_samples = get_cpu_usage_samples()

    mean = mn(cpu_usage_samples)

    mean_with_noise = round(  # type: ignore
        dp.mean(  # type: ignore
            cpu_usage_samples,
            epsilon=0.5,  # Privacy parameter controlling the level of differential privacy
            bounds=(0, 100),  # Assumed bounds for CPU usage percentage (0-100%)
        ),
        2,  # Round to 2 decimal places
    )

    # Saving Mean with Noise added in it.
    public_mean_file: Path = restricted_public_folder / "cpu_tracker.json"
    save(path=str(public_mean_file), cpu_usage=mean_with_noise)

    # Saving the actual private mean.
    private_mean_file: Path = private_folder / "cpu_tracker.json"
    save(path=str(private_mean_file), cpu_usage=mean)

if __name__ == "__main__":
    client = Client.load()
    main()
