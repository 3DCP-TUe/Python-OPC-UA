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
from asyncua import Server, ua

async def main():
    
    # Setup the server
    logging.info("Starting the OPC UA server.")
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/example/")
    server.set_server_name("OPC UA server example")

    # Set up the name space
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Populate
    myobj = await server.nodes.objects.add_object(idx, "Values")
    myvar1 = await myobj.add_variable(idx, "Value 1", 10.0, varianttype=ua.VariantType.Double)
    myvar2 = await myobj.add_variable(idx, "Value 2", 20.0, varianttype=ua.VariantType.Double)
    myvar3 = await myobj.add_variable(idx, "Value 3", 30.0, varianttype=ua.VariantType.Double)

    # Node ID
    logging.info("Object info           : {}".format(myobj))
    logging.info("Node ID of 'value 1'  : {}".format(myvar1.nodeid.to_string()))
    logging.info("Node ID of 'value 2'  : {}".format(myvar2.nodeid.to_string()))
    logging.info("Node ID of 'value 3'  : {}".format(myvar3.nodeid.to_string()))
    
    # Value counters
    counter1 = 10.0
    counter2 = 20.0
    counter3 = 30.0

    async with server:
        
        while True:
            
            logging.info("The OPC UA server is still running...")
            
            await myvar1.write_value(counter1)
            await myvar2.write_value(counter2)
            await myvar3.write_value(counter3)
            
            counter1 += 1
            counter2 += 1
            counter3 += 1

            await asyncio.sleep(1.0)


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=False)