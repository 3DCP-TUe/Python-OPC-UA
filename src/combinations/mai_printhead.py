# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of Python-OPC-UA.
# Project: https://github.com/3DCP-TUe/Python-OPC-UA
#
# Copyright (c) 2024-2025 3D Concrete Printing Research Group at Eindhoven University of Technology
#
# Authors:
#   - Arjen Deetman (2024-2025)
#
# For license details, see the LICENSE file in the project root.

import asyncio
import logging
from asyncua import Client, ua

SPEED1 = 2100 # cHz
SPEED2 = 4200 # cHz
MAI_PUMP_SPEED = [SPEED1, SPEED1, SPEED1, SPEED1, SPEED1, SPEED1, SPEED2, SPEED2, SPEED2, SPEED2, SPEED2, SPEED2, SPEED1, SPEED1, SPEED1, SPEED1, SPEED1, SPEED1, SPEED2, SPEED2, SPEED2, SPEED2, SPEED2, SPEED2, SPEED1]
PRINTHEAD_VELOCITY = [51, 100, 150, 50, 300, 225, 51, 100, 50, 300, 225, 150, 51, 150, 300, 50, 100, 225, 51, 225, 50, 300, 100, 150, 51]
DELTA_TIME = 10.0 # Minutes

async def main():
  
    while True:
        
        # Data check
        if (len(PRINTHEAD_VELOCITY) != len(MAI_PUMP_SPEED)):
            logging.error("List lenghts are not equal.")
            break
        
        n = len(PRINTHEAD_VELOCITY)
        mai = Client(url="opc.tcp://10.129.4.80:48010")
        printhead = Client(url="opc.tcp://10.129.4.20:4840")

        try:
            async with mai, printhead:
                
                logging.info("Get nodes")
                node_printhead_velocity = printhead.get_node("ns=3;s=\"Velocity_Jog_left\"")
                node_mai_pump_speed =  mai.get_node("ns=2;s=Tags.GECO/MPRX_EXT_Pump_Speed_cHz_I")
                
                logging.info("Start")
                
                for i in range(n):
                    
                    # Get values
                    printhead_rpm = PRINTHEAD_VELOCITY[i]
                    mai_pump_speed = MAI_PUMP_SPEED[i]

                    # Log
                    logging.info("Settings: {}, {}, {}, {}".format(i, n, printhead_rpm, mai_pump_speed))

                    # Write values
                    value1 = ua.DataValue(ua.Variant(printhead_rpm, ua.VariantType.Double))
                    value2 = ua.DataValue(ua.Variant(mai_pump_speed, ua.VariantType.Int16))

                    await node_printhead_velocity.write_value(value1)
                    await node_mai_pump_speed.write_value(value2)

                    # Wait
                    await asyncio.sleep(DELTA_TIME*60)
                    
                    # Check connections
                    await mai.check_connection()
                    await printhead.check_connection()

        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())