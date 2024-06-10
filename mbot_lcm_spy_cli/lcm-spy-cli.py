import lcm
import time
from collections import defaultdict
from threading import Thread, Event
import argparse
import importlib

# Command-line argument parsing
parser = argparse.ArgumentParser(description="LCM Spy CLI")
parser.add_argument("--channels", type=str, help="Comma-separated list of channel names to print decoded messages")
parser.add_argument("--rate", type=float, default=1, help="Rate at which data is printed in Hz (default: 1 Hz)")
parser.add_argument("--module", type=str, help="Module to use for decoding messages")
args = parser.parse_args()

# Parse channels from the --channels argument
channels_to_print = []
if args.channels:
    channels_to_print = args.channels.split(',')

# Load the module for decoding messages if provided
decode_module = None
if args.module:
    try:
        decode_module = importlib.import_module(args.module)
    except ImportError:
        print(f"Error: Could not import module {args.module}")
        decode_module = None

# Data structures to hold message counts, timestamps, and LCM types
message_counts = defaultdict(int)
message_times = defaultdict(list)
channel_types = {}
stop_event = Event()
decoded_message_dict = defaultdict(list)

def message_handler(channel, data):
    global message_counts, message_times, channel_types, decoded_message_dict
    
    msg_time = int(time.time())
    
    lcm_type = "Unknown"
    decoded_message = None
    if decode_module:
        try:
            # Attempt to decode the message to find its type
            for attr in dir(decode_module):
                lcm_type_class = getattr(decode_module, attr)
                if isinstance(lcm_type_class, type) and hasattr(lcm_type_class, 'decode'):
                    try:
                        lcm_type_instance = lcm_type_class.decode(data)
                        lcm_type = lcm_type_class.__name__
                        decoded_message = lcm_type_instance
                        break
                    except Exception:
                        continue
        except Exception as e:
            lcm_type = f"Error: {e}"

    # Store the decoded message fields if the channel matches any of the specified channels
    if channel in channels_to_print and decoded_message:
        decoded_message_dict[channel] = [(field, getattr(decoded_message, field)) for field in decoded_message.__slots__]
    
    # Update message counts and times
    message_counts[channel] += 1
    message_times[channel].append(time.time())
    channel_types[channel] = lcm_type

def print_status():
    while not stop_event.is_set():
        time.sleep(1 / args.rate)  # Update at the specified rate
        print("\033[H\033[J", end="")  # Clear the screen
        print(f"{'Channel':<20} {'Type':<20} {'Rate':<10} {'Msgs Rcvd':<10}")
        print("="*60)
        for channel, times in message_times.items():
            current_time = time.time()
            # Filter times to keep only those within the last second
            times = [t for t in times if current_time - t < 1]
            message_times[channel] = times
            rate = len(times) / 1.0
            total_messages = message_counts[channel]
            lcm_type = channel_types.get(channel, "Unknown")
            print(f"{channel:<20} {lcm_type:<20} {rate:<10.2f} {total_messages:<10}")
        
        for channel in channels_to_print:
            if channel in decoded_message_dict:
                print(f"\nDecoded message on channel {channel}:")
                print(f"{'Field':<20} {'Value':<20}")
                print("="*40)
                for field, value in decoded_message_dict[channel]:
                    print(f"{field:<20} {str(value):<20}")

def lcm_handle_loop(lc):
    while not stop_event.is_set():
        try:
            lc.handle_timeout(1000)  # Timeout set to 1000ms
        except Exception as e:
            print(f"Error in LCM handle loop: {e}")

if __name__ == "__main__":
    lc = lcm.LCM()

    # Subscribe to all LCM channels
    subscription = lc.subscribe(".*", message_handler)

    # Start the status printing thread
    status_thread = Thread(target=print_status)
    status_thread.daemon = True
    status_thread.start()

    # Start the LCM handle loop
    lcm_thread = Thread(target=lcm_handle_loop, args=(lc,))
    lcm_thread.daemon = True
    lcm_thread.start()
    
    try:
        while True:
            time.sleep(1)  # Main thread sleep
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
        stop_event.set()
        lcm_thread.join()
        status_thread.join()
        lc.unsubscribe(subscription)
        print("Exited cleanly.")
