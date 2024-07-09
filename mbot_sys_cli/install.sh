#!/bin/bash
set -e  # Quit on error.

# Install mbot-lcm-spy
echo "Installing mbot-lcm-spy..."
chmod +x mbot_lcm_spy/mbot_lcm_spy.py
sudo cp mbot_lcm_spy/mbot_lcm_spy.py /usr/local/bin/mbot-lcm-spy

# Install system tool mbot-service
echo "Installing mbot-service..."
chmod +x mbot_service/mbot-service.sh
sudo cp mbot_service/mbot-service.sh /usr/local/bin/mbot-service

# Install mbot-lcm-msg
echo "Installing mbot-lcm-msg..."
chmod +x mbot_lcm_msg/mbot_lcm_msg.py
sudo cp mbot_lcm_msg/mbot_lcm_msg.py /usr/local/bin/mbot-lcm-msg

# Install dispatcher script mbot
echo "Installing mbot cli tools..."
chmod +x mbot.sh
sudo cp mbot.sh /usr/local/bin/mbot