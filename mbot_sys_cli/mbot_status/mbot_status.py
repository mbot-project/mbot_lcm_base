#!/usr/bin/env python3
import argparse
import textwrap
import lcm
import time
import sys
import subprocess
from mbot_lcm_msgs.mbot_analog_t import mbot_analog_t
from mbot_lcm_msgs.mbot_imu_t import mbot_imu_t
from mbot_lcm_msgs.lidar_t import lidar_t
import threading

# Define variables
RATE = 1

# Command-line argument parsing
parser = argparse.ArgumentParser(description="MBot Status")
parser.add_argument(
    "--topic", 
    type=str, 
    help="Topic to monitor (default: all topics). Available topics: battery, temperature, test."
)
parser.add_argument(
    "--continuous", 
    action="store_true", 
    help="Continue monitoring status until interrupted (e.g., with Ctrl+C)."
)
parser.add_argument(
    "--verbose", 
    action="store_true", 
    help="Provide detailed information (only valid if --topic is specified)."
)
args = parser.parse_args()

# Custom validation
if args.verbose and not args.topic:
    parser.error("--verbose can only be used if --topic is specified")


class LCMFetch:
    def __init__(self):
        self.battery_voltage = -1
        self.imu_readings = []
        self.lidar_num_ranges = -1
        self.initialized = {"battery": False, 
                            "imu": False, 
                            "lidar": False}

        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=0")

        # subscriber
        self.lc.subscribe("MBOT_ANALOG_IN", self.battery_info_callback)
        self.lc.subscribe("MBOT_IMU", self.imu_info_callback)
        self.lc.subscribe("LIDAR", self.lidar_info_callback)

        # Start a thread to handle LCM messages continuously
        self.lcm_thread = threading.Thread(target=self.lcm_handler, daemon=True)
        self.lcm_thread.start()

        # lcm time 
        self.battery_lcm_time = 0
        self.imu_lcm_time = 0
        self.lidar_lcm_time = 0

    def lcm_handler(self):
        while True:
            # Wait for a message for up to 1 second
            self.lc.handle_timeout(1000)

    def battery_info_callback(self, channel, data):
        battery_info = mbot_analog_t.decode(data)
        self.battery_voltage = battery_info.volts[3]
        self.initialized["battery"] = True
        self.battery_lcm_time = time.time()

    def imu_info_callback(self, channel, data):
        imu_reading = mbot_imu_t.decode(data)
        roll, pitch, yaw = imu_reading.angles_rpy
        self.imu_readings = [roll, pitch, yaw]
        self.initialized["imu"] = True
        self.imu_lcm_time = time.time()

    def lidar_info_callback(self, channel, data):
        lidar_reading = lidar_t.decode(data)
        num_ranges = lidar_reading.num_ranges
        self.lidar_num_ranges = num_ranges
        self.initialized["lidar"] = True
        self.lidar_lcm_time = time.time()

    def battery_test(self):
        if (time.time() - self.battery_lcm_time) > 1:
            self.battery_voltage = -1
        return self.battery_voltage

    def imu_test(self):
        if (time.time() - self.imu_lcm_time) > 1:
            self.imu_readings = []
            return False
        
        if self.imu_readings != []:
            return any(element != 0.0 for element in self.imu_readings)
        
        return False

    def lidar_test(self):
        if (time.time() - self.lidar_lcm_time) > 1:
            self.lidar_num_ranges = -1
            return False
        
        if self.lidar_num_ranges < 250:
            return False
        return True
        
    def get_status(self):
        status_dict = {
            "battery": self.battery_test(),
            "imu_test": self.imu_test(),
            "lidar": self.lidar_test()
        }
        return status_dict

    def is_initialized(self):
        # Check if all necessary data has been received
        return all(self.initialized.values())

def get_temperature():
    try:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        temp_output = result.stdout.strip()
        temp_value = temp_output.split("=")[1].split("'")[0]
        return float(temp_value)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return -1

def get_usb_connection(usb_device_dict):
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
        lsusb_output = result.stdout.strip()

        usb_device_dict["pico"] = any("Pi Pico" in line for line in lsusb_output.splitlines())
        usb_device_dict["lidar"] = any("CP210x UART Bridge" in line for line in lsusb_output.splitlines())

        return usb_device_dict

    except Exception as e:
        print(f"Error checking USB devices: {e}")
        return usb_device_dict

def print_battery(battery_voltage):
    # Print the battery voltage in an aligned format
    print(f"{'Battery Voltage:':<20} {battery_voltage:.2f} V")

    # Nicely formatted voltage table for verbose output
    voltage_table = """
        Battery Information:
        - Voltage = -1           : No message received
        - Voltage in (0, 1.5)    : Missing jumper cap
        - Voltage in (3.5, 5.5)  : Barrel plug is unplugged
        - Voltage in (6, 7)      : Jumper cap is on 6 V
        - Voltage in (7, 12)     : Jumper cap is on 12 V
        """
    if args.topic and args.verbose:
        print(textwrap.dedent(voltage_table))

def print_temperature(temperature):
    print(f"{'Temperature:':<20} {temperature:<.2f} C")

def print_imu_test(imu_test, imu_readings):
    if imu_test:
        status_text = f"{'Pass':<10}"
        imu_status_colored = f"\033[92m{status_text}\033[0m"  # Green text
    else:
        status_text = f"{'Fail':<10}"
        imu_status_colored = f"\033[91m{status_text}\033[0m"  # Red text

    print(f"{'IMU Test:':<20} {imu_status_colored}")
    if args.verbose and not imu_test:
        formatted_readings = ", ".join(f"{reading:.2f}" for reading in imu_readings)
        note = (
           f"   IMU readings (roll, pitch, yaw) are [{formatted_readings}]. Possible causes:\n"
            "   - Bottom board may be disconnected. \n"
            "   - LCM server might be experiencing a glitch. Press RST button on Pico. \n"
            "   - IMU may be broken."
        )
        print(f"Note:\n{note}")

def print_usb_devices(usb_devices):
    # Print status for Pico
    if not usb_devices.get("pico", False):
        status_text = f"{'Disconnected':<15}"
        print(f"{'Pico Board:':<20} \033[91m{status_text}\033[0m")
        if args.verbose:
            note = (
                "    The Pico board is not recognized by CLI lsusb. Possible causes:\n"
                "    - USB Type-C cable is not connected or faulty.\n"
                "    - Battery is low."
            )
            print(f"Note:\n{note}")
    else:
        status_text = f"{'Connected':<15}"
        print(f"{'Pico Board:':<20} \033[92m{status_text}\033[0m")

    # Print status for Lidar
    if not usb_devices.get("lidar", False):
        status_text = f"{'Disconnected':<15}"
        print(f"{'Lidar:':<20} \033[91m{status_text}\033[0m")
        if args.verbose:
            note = (
                "    The Lidar is not recognized by CLI lsusb. Possible causes:\n"
                "    - USB cable is not connected or faulty.\n"
                "    - Battery is low."
            )
            print(f"Note:\n{note}")
    else:
        status_text = f"{'Connected':<15}"
        print(f"{'Lidar:':<20} \033[92m{status_text}\033[0m")

def print_lidar_test(lidar_test):
    if lidar_test:
        status_text = f"{'Pass':<10}"
        imu_status_colored = f"\033[92m{status_text}\033[0m"  # Green text
    else:
        status_text = f"{'Fail':<10}"
        imu_status_colored = f"\033[91m{status_text}\033[0m"  # Red text

    print(f"{'Lidar Test:':<20} {imu_status_colored}")
    if args.verbose and not lidar_test:
        note = (
            "   LiDAR number of ranges < 250. Possible causes:\n"
            "   - LiDAR Disconnected. \n"
            "   - LiDAR might broken."
        )
        print(f"Note:\n{note}") 

if __name__ == "__main__":
    lcm_fetched_status = LCMFetch()
    usb_devices = {
        "pico": False,
        "lidar": False
    }

    # Wait until the LCM messages are received
    past_time = time.time()
    while not lcm_fetched_status.is_initialized():
        time.sleep(0.1)
        if time.time() - past_time > 1:
            break 

    if args.topic:
        if args.topic == "battery":
            while True:
                status_dict = lcm_fetched_status.get_status()
                print_battery(status_dict['battery'])
                if not args.continuous:
                    break
                time.sleep(1 / RATE)
        elif args.topic == "temperature":
            while True:
                temperature = get_temperature()
                print_temperature(temperature)
                if not args.continuous:
                    break
                time.sleep(1 / RATE)
        elif args.topic == "test":
            while True:
                status_dict = lcm_fetched_status.get_status()
                usb_devices = get_usb_connection(usb_devices)
                print_usb_devices(usb_devices)
                print_imu_test(status_dict['imu_test'], lcm_fetched_status.imu_readings)
                print_lidar_test(status_dict['lidar'])
                if not args.continuous:
                    break
                print("\033[H\033[J", end="")  # Clear the screen
                time.sleep(1 / RATE)
    else:
        while True:
            status_dict = lcm_fetched_status.get_status()
            temperature = get_temperature()
            usb_devices = get_usb_connection(usb_devices)
            # Print the status information
            print_battery(status_dict['battery'])
            print_temperature(temperature)
            print_usb_devices(usb_devices)
            print_imu_test(status_dict['imu_test'], lcm_fetched_status.imu_readings)
            print_lidar_test(status_dict['lidar'])
            if not args.continuous:
                break
            print("\033[H\033[J", end="")  # Clear the screen
            time.sleep(1 / RATE)
