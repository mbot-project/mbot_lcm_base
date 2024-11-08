#ifndef LCM_CONFIG_H
#define LCM_CONFIG_H


#define MULTICAST_URL "udpm://239.255.76.67:7667?ttl=0"

/////// LCM channels //////
#define MBOT_TIMESYNC_CHANNEL "MBOT_TIMESYNC"
#define MBOT_ODOMETRY_CHANNEL "MBOT_ODOMETRY"
#define MBOT_ODOMETRY_RESET_CHANNEL "MBOT_ODOMETRY_RESET"
#define MBOT_MOTOR_PWM_CMD_CHANNEL "MBOT_MOTOR_PWM_CMD"
#define MBOT_MOTOR_PWM_CHANNEL "MBOT_MOTOR_PWM"
#define MBOT_MOTOR_VEL_CMD_CHANNEL "MBOT_MOTOR_VEL_CMD"
#define MBOT_MOTOR_VEL_CHANNEL "MBOT_MOTOR_VEL"
#define MBOT_VEL_CMD_CHANNEL "MBOT_VEL_CMD"
#define MBOT_VEL_CHANNEL "MBOT_VEL"
#define MBOT_ANALOG_CHANNEL "MBOT_ANALOG_IN"
#define MBOT_IMU_CHANNEL "MBOT_IMU"
#define MBOT_ENCODERS_CHANNEL "MBOT_ENCODERS"
#define MBOT_ENCODERS_RESET_CHANNEL "MBOT_ENCODERS_RESET"
#define MBOT_APRILTAG_ARRAY_CHANNEL "MBOT_APRILTAG_ARRAY"

/////// serial channels //////
enum message_topics{
    MBOT_TIMESYNC = 201, 
    MBOT_ODOMETRY = 210, 
    MBOT_ODOMETRY_RESET = 211,
    MBOT_VEL_CMD = 214,
    MBOT_IMU = 220,
    MBOT_ENCODERS = 221,
    MBOT_ENCODERS_RESET = 222,
    MBOT_ANALOG_IN = 223,
    MBOT_MOTOR_PWM_CMD = 230,
    MBOT_MOTOR_VEL_CMD = 231,
    MBOT_MOTOR_VEL = 232,
    MBOT_MOTOR_PWM = 233,
    MBOT_VEL = 234,
    MBOT_APRILTAG_ARRAY = 235
};

#endif // LCM_CONFIG_H
