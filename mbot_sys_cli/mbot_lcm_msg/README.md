> This tool is similar to rosmsg, used to inspect the data structure of MBot LCM messages. Though rosmsg is deprecated in ROS 2 now.

## Install
> If you have run the install.sh in the home folder, then you don't need the following commands.

```bash
chmod +x mbot_lcm_msg.py
sudo cp mbot_lcm_msg.py /usr/local/bin/mbot-lcm-msg
```

## Usage
```
mbot lcm-msg [-h] [--module MODULE] {show,list} ...

positional arguments:
  {show,list}      sub-command help
    show           Output the message definition
    list           List all available LCM messages

options:
  -h, --help       show this help message and exit
  --module MODULE  Module to use for decoding messages
```

Example:
```bash
# this will print all the mbot lcm message's type
mbot lcm-msg list

# this will print pose3D_t data structure
mbot lcm-msg show pose3D_t

# this will print pose3D_t and pose2D_t data structure
mbot lcm-msg show pose3D_t,pose2D_t
```