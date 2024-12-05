#!/usr/bin/env python3
import argparse
import lcm
import time
import sys
import subprocess

# Command-line argument parsing
parser = argparse.ArgumentParser(description="MBot Status")
parser.add_argument("--topic", type=str, help="Topic to monitor (default: all topics)")
parser.add_argument("--continuous", action="store_true", help="Continue monitoring status (until Ctrl+C)")
args = parser.parse_args()

class MBotBatteryStatus:
    def __init__(self):
        # Set up LCM if available
        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=0")
        self.battery_voltage = -1
        self.mbot_lcm_installed = self.check_mbot_lcm_installed()
        if self.mbot_lcm_installed:
            self.lc.subscribe("MBOT_ANALOG_IN", self.battery_info_callback)

    def check_mbot_lcm_installed(self):
        try:
            from mbot_lcm_msgs.mbot_analog_t import mbot_analog_t
            self.mbot_analog_t = mbot_analog_t
            return True
        except ImportError:
            self.battery_voltage = -2  # error code
            print("Error: mbot_lcm_msgs not installed.")
            return False
          
    def battery_info_callback(self, channel, data):
        battery_info = self.mbot_analog_t.decode(data)
        self.battery_voltage = battery_info.volts[3]
    
    def get_battery_status(self):
        if self.lc:
            # Wait for a message for up to 1 second
            self.lc.handle_timeout(1000)
        return self.battery_voltage

def get_temperature():
    try:
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        temp_output = result.stdout.strip()
        temp_value = temp_output.split("=")[1].split("'")[0]
        return float(temp_value)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return -1
        
if __name__ == "__main__":
    mbot_battery_status = MBotBatteryStatus()
    battery_voltage = mbot_battery_status.get_battery_status()
    temperature = get_temperature()

    if args.topic:
        if args.topic == "battery":
            print(f"Battery Voltage: {battery_voltage:.2f} V")
            if args.continuous:
                while True:
                    print("\033[H\033[J", end="")  # Clear the screen
                    battery_voltage = mbot_battery_status.get_battery_status()
                    print(f"Battery Voltage: {battery_voltage:.2f} V")
    else:
        print(f"Battery Voltage: {battery_voltage:.2f} V")
        print(f"Temperature: {temperature:.2f} °C")