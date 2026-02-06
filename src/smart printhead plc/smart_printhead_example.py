"""
This file is part of the Python OPC UA examples of Eindhoven University of Technology. 
The files of this project are licensed under the terms of GNU General Public License 
version 3.0 (GPL v3.0) as published by the Free Software Foundation. For more information 
and the LICENSE file, see <https://github.com/3DCP-TUe/Python-OPC-UA>.
"""

import asyncio
import logging
from asyncua import Client, ua

async def main():
  
    while True:

        client = Client(url="opc.tcp://10.129.4.20:4840")

        try:
            async with client:

                node_motor_1_velocity = client.get_node("ns=3;s=\"Velocity_Jog_left\"")
                            
                while True: 
                    
                    # Write value: motor 1 RPM
                    value = ua.DataValue(ua.Variant(100, ua.VariantType.Double))
                    await node_motor_1_velocity.write_value(value)

                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws a exception if connection is lost

        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())