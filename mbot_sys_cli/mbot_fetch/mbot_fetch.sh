#!/bin/bash

# Path to your ASCII art file
# ascii_art_file="mbot_ascii.txt"

# Define colors
blue_bold='\033[1;34m'  # Blue color, bold text
maize='\033[38;2;255;203;5m'
reset='\033[0m'         # Reset color and formatting

# Get system information
mbot_name=$(hostname)
wifi_name=$(iwgetid -r)
model_name=$(cat /proc/device-tree/model | tr -d '\0')
os_name=$(cat /etc/os-release | grep "^PRETTY_NAME=" | cut -d '"' -f 2)
kernel_version=$(uname -r)
uptime_info=$(uptime -p)
shell_name=$(basename $SHELL)
memory_info=$(free -h | awk '/^Mem:/{print $3 " / " $2}')
storage_info=$(df -h / | awk 'NR==2 {print $3 " / " $2 " (" $5 " used)"}')

# Read firmware and calibration versions from ~/.mbot_info.txt
firmware_version="N/A"
calibration_version="N/A"

if [ -f ~/.mbot_info.txt ]; then
    read_firmware_version=$(grep "^mbot_firmware:" ~/.mbot_info.txt | cut -d ' ' -f 2)
    read_calibration_version=$(grep "^mbot_calibration:" ~/.mbot_info.txt | cut -d ' ' -f 2)

    # Use the read values only if they are not empty
    if [ -n "$read_firmware_version" ]; then
        firmware_version=$read_firmware_version
    fi

    if [ -n "$read_calibration_version" ]; then
        calibration_version=$read_calibration_version
    fi
fi

echo -e "${maize}"
# cat "$ascii_art_file"
cat <<'EOF'
███╗   ███╗██████╗  ██████╗ ████████╗
████╗ ████║██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║██████╔╝██║   ██║   ██║   
██║╚██╔╝██║██╔══██╗██║   ██║   ██║   
██║ ╚═╝ ██║██████╔╝╚██████╔╝   ██║   
╚═╝     ╚═╝╚═════╝  ╚═════╝    ╚═╝   
EOF
echo -e "${reset}"

# Print the information with bold blue labels
echo -e "${blue_bold}MBot Name:${reset} ${mbot_name}"
echo -e "${blue_bold}Wifi Name:${reset} ${wifi_name}"
echo -e "${blue_bold}Model:${reset} ${model_name}"
echo -e "${blue_bold}OS:${reset} ${os_name}"
echo -e "${blue_bold}Kernel:${reset} ${kernel_version}"
echo -e "${blue_bold}Uptime:${reset} ${uptime_info}"
echo -e "${blue_bold}Shell:${reset} ${shell_name}"
echo -e "${blue_bold}Memory:${reset} ${memory_info}"
echo -e "${blue_bold}Storage:${reset} ${storage_info}"
echo -e "${blue_bold}Firmware Version:${reset} ${firmware_version}"
echo -e "${blue_bold}Calibration Version:${reset} ${calibration_version}"
