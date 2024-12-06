> This tool is to check mbot status in real time

### Usage

```
mbot status [-h] [--topic TOPIC] [--continuous] [--verbose]
```

```bash
$ mbot status -h
usage: mbot status [-h] [--topic TOPIC] [--continuous] [--verbose]

MBot Status

options:
  -h, --help     show this help message and exit
  --topic TOPIC  Topic to monitor (default: all topics)
  --continuous   Continue monitoring status (until Ctrl+C)
  --verbose      Give details (only valid if --topic is specified)
```
- Available topic: `battery`, `temperature`, `test`

For example:
```bash
$ mbot status
---
Battery Voltage:     11.33 V
Temperature:         52.70 C
Bottom Board:        Connected      
IMU Test:            Pass  
```
```bash
$ mbot status --topic test --verbose
---
Bottom Board:        Connected      
IMU Test:            Pass
```
```bash
$ mbot status --topic test --verbose
---
Bottom Board:        Disconnected   
Note:
    No LCM message received from the bottom board. Possible causes:
    - USB Type-C cable is not connected.
    - LCM Serial Server is not running.
IMU Test:            Fail      
Note:
   IMU readings (roll, pitch, yaw) are all 0. Possible causes:
   - IMU may be broken.
   - Bottom board may be disconnected.
```