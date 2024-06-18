# Just to test if mbot-lcm-spy can take nested lcm struct

import lcm
import time
from mbot_lcm_msgs.mbot_apriltag_array_t import mbot_apriltag_array_t
from mbot_lcm_msgs.mbot_apriltag_t import mbot_apriltag_t

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=0")

msg = mbot_apriltag_array_t()
msg.array_size = 2
msg.detections = []

apriltag1 = mbot_apriltag_t()
apriltag1.tag_id = 1
apriltag1.pose.x = 1
apriltag1.pose.y = 2
apriltag1.pose.z = 3
apriltag1.pose.angles_rpy = [1.0, 2.1, 3.1]
apriltag1.pose.angles_quat = [1, 2, 3, 4]
msg.detections.append(apriltag1)

apriltag2 = mbot_apriltag_t()
apriltag2.tag_id = 2
apriltag2.pose.x = 1
apriltag2.pose.y = 2
apriltag2.pose.z = 3
apriltag2.pose.angles_rpy = [1.0, 2.1, 3.1]
apriltag2.pose.angles_quat = [1, 2, 3, 4]
msg.detections.append(apriltag2)

try:
    while True:
        lc.publish("MBOT_APRILTAG_ARRAY", msg.encode())
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")

