#!/usr/bin/env python3
import argparse
import textwrap
import lcm
import time
import sys
import subprocess
from mbot_lcm_msgs.mbot_analog_t import mbot_analog_t
from mbot_lcm_msgs.mbot_imu_t import mbot_imu_t
import threading

# Define variables
RATE = 1

# Command-line argument parsing
parser = argparse.ArgumentParser(description="MBot Status")
parser.add_argument("--topic", type=str, help="Topic to monitor (default: all topics)")
parser.add_argument("--continuous", action="store_true", help="Continue monitoring status (until Ctrl+C)")
parser.add_argument("--verbose", action="store_true", help="Give details (only valid if --topic is specified)")
args = parser.parse_args()

# Custom validation
if args.verbose and not args.topic:
    parser.error("--verbose can only be used if --topic is specified")


class LCMFetch:
    def __init__(self):
        self.battery_voltage = -1
        self.imu_readings = []
        self.initialized = {"battery": False, "imu": False}
        self.bottom_board_connected = False

        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=0")

        # subscriber
        self.lc.subscribe("MBOT_ANALOG_IN", self.battery_info_callback)
        self.lc.subscribe("MBOT_IMU", self.imu_info_callback)

        # Start a thread to handle LCM messages continuously
        self.lcm_thread = threading.Thread(target=self.lcm_handler, daemon=True)
        self.lcm_thread.start()

    def lcm_handler(self):
        while True:
            # Wait for a message for up to 1 second
            past_time = time.time()
            self.lc.handle_timeout(1000)
            if time.time() - past_time > 1:
                self.reset_variables()

    def battery_info_callback(self, channel, data):
        battery_info = mbot_analog_t.decode(data)
        self.battery_voltage = battery_info.volts[3]
        self.initialized["battery"] = True
        self.bottom_board_connected = True

    def imu_info_callback(self, channel, data):
        imu_reading = mbot_imu_t.decode(data)
        roll, pitch, yaw = imu_reading.angles_rpy
        self.imu_readings = [roll, pitch, yaw]
        self.initialized["imu"] = True

    def imu_test(self):
        if self.imu_readings != []:
            return any(element > 0.0 for element in self.imu_readings)
        return False

    def get_status(self):
        imu_test = "Pass" if self.imu_test() else "Fail"

        status_dict = {
            "battery": self.battery_voltage,
            "imu_test": imu_test
        }
        return status_dict

    def is_initialized(self):
        # Check if all necessary data has been received
        return all(self.initialized.values())

    def reset_variables(self):
        self.battery_voltage = -1
        self.imu_readings = []
        self.bottom_board_connected = False

def get_temperature():
    try:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        temp_output = result.stdout.strip()
        temp_value = temp_output.split("=")[1].split("'")[0]
        return float(temp_value)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return -1
    
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

def print_imu_test(imu_test):
    status_text = f"{imu_test:<10}"  # Align to the left

    # Set status color and note based on imu_test result
    if imu_test == "Pass":
        imu_status_colored = f"\033[92m{status_text}\033[0m"  # Green text
    else:
        imu_status_colored = f"\033[91m{status_text}\033[0m"  # Red text

    print(f"{'IMU Test:':<20} {imu_status_colored}")
    if args.verbose and imu_test == "Fail":
        note = (
            "   IMU readings (roll, pitch, yaw) are all 0. Possible causes:\n"
            "   - IMU may be broken.\n"
            "   - Bottom board may be disconnected."
        )
        print(f"Note:\n{note}")

def print_bottom_board(bottom_board_connected):
    if not bottom_board_connected:
        status_text = f"{'Disconnected':<15}"  # Align to the left
        print(f"{'Bottom Board:':<20} \033[91m{status_text}\033[0m")  # Red text
        if args.verbose:
            note = (
                "    No LCM message received from the bottom board. Possible causes:\n"
                "    - USB Type-C cable is not connected.\n"
                "    - LCM Serial Server is not running."
            )
            print(f"Note:\n{note}")
    else:
        status_text = f"{'Connected':<15}"  # Align to the left
        print(f"{'Bottom Board:':<20} \033[92m{status_text}\033[0m")  # Green text


if __name__ == "__main__":
    lcm_fetched_status = LCMFetch()

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
                print_bottom_board(lcm_fetched_status.bottom_board_connected)
                print_imu_test(status_dict['imu_test'])
                if not args.continuous:
                    break
                print("\033[H\033[J", end="")  # Clear the screen
                time.sleep(1 / RATE)
    else:
        while True:
            status_dict = lcm_fetched_status.get_status()
            temperature = get_temperature()

            # Print the status information
            print_battery(status_dict['battery'])
            print_temperature(temperature)
            print_bottom_board(lcm_fetched_status.bottom_board_connected)
            print_imu_test(status_dict['imu_test'])
            if not args.continuous:
                break
            print("\033[H\033[J", end="")  # Clear the screen
            time.sleep(1 / RATE)
