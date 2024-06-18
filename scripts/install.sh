#!/bin/bash
set -e  # Quit on error.

# Build the code.
echo "Building the code..."
echo
if [ ! -d "build/" ]; then
    mkdir build
fi
cd build
cmake ..
make
sudo make install
cd ..

# Install mbot-lcm-spy
echo "Installing mbot-lcm-spy..."
chmod +x mbot_lcm_spy/mbot_lcm_spy.py
sudo cp mbot_lcm_spy/mbot_lcm_spy.py /usr/local/bin/mbot-lcm-spy

# Install the serial service.
LCM_SERIAL_SRV_PATH=mbot_lcm_serial/services/
LCM_SERIAL_SRV_NAME=mbot-lcm-serial.service
echo
echo "Installing $LCM_SERIAL_SRV_NAME..."

# Install services.
sudo cp $LCM_SERIAL_SRV_PATH/$LCM_SERIAL_SRV_NAME /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $LCM_SERIAL_SRV_NAME
sudo systemctl restart $LCM_SERIAL_SRV_NAME

# Insert line for classpath into bashrc
echo 'export CLASSPATH=$CLASSPATH:"/usr/local/share/java/mbot_lcm_msgs.jar"' >> ~/.bashrc

echo
echo "Done!"
