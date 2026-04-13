#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2025 Jecjune. All rights reserved.
# Author: Jecjune zejun.chen@hexfellow.com
# Date  : 2025-8-1
################################################################

# A Simple Test for HexDeviceApi
# Quick Start: python3 tests/chassis_test.py --url ws://<Your controller ip>:8439 or ws://[::1%eth0]:8439

import sys
import argparse
import numpy as np
import time

import hex_device
from hex_device import HexDeviceApi, public_api_types_pb2
from hex_device import Chassis, Imu, Gamepad
from hex_device.motor_base import CommandType, SpeedWithMaxCurrentMotorCommand


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Hexapod robotic arm trajectory planning and execution test',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--url', 
        metavar='URL',
        default="ws://0.0.0.0:8439",
        help='WebSocket URL for HEX device connection, example: ws://0.0.0.0:8439 or ws://[::1%%eth0]:8439'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level for hex_device package, example: DEBUG, INFO, WARNING, ERROR'
    )
    args = parser.parse_args()
    
    # Set log level
    hex_device.set_log_level(args.log_level)
    print(f"Log level set to: {args.log_level}")
    
    # Init HexDeviceApi
    api = HexDeviceApi(ws_url=args.url, control_hz=500, enable_kcp=True, local_port=0)
    first_time = True
    
    try:
        while True:
            if api.is_api_exit():
                print("Public API has exited.")
                break
            else:
                for device in api.device_list:
                    # for ChassisMaver
                    if isinstance(device, Chassis):
                        if device.has_new_data():
                            if first_time:
                                first_time = False
                                # Must start device before using it.
                                device.start()
                                device.clear_odom_bias()

                            # device.get_device_summary()
                            
                            speed_with_current = SpeedWithMaxCurrentMotorCommand(0.5,6.0)
                            
                            # device.set_vehicle_speed(0.0, 0.0, 0.1)
                            device.motor_command(CommandType.SPEED_WITH_MAX_CURRENT, [speed_with_current] * device.motor_count)

                            torques = [ i.tolist() for i in device.get_motor_torques()]
                            
                            if torques is not None:
                                print(f"torques: {torques}")
            
            
            time.sleep(0.0001)

    except KeyboardInterrupt:
        print("Received Ctrl-C.")
        device.motor_command(CommandType.BRAKE, [True] * device.motor_count)
        api.close()
    finally:
        pass

    print("Resources have been cleaned up.")
    exit(0)


if __name__ == "__main__":
    main()
