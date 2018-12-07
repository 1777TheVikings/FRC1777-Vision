from typing import Any, NoReturn, List
from numpy import ndarray
from networktables import NetworkTables
import asyncio
import xml.etree.ElementTree as ElementTree
import logging

from base_classes import PostProcessorBase


class NetworkTablesPostProcessor(PostProcessorBase):
    """
    Outputs data to a NetworkTables server.
    
    The following keys will be defined in the table:
    
    - `vision_value` (number): The first data point returned by the processor.
    
    - `vision_new_value` (boolean): If true, the value has been updated. If you use this, make sure to set this to
    false after reading it on the server side.
    
    - `vision_shutdown` (boolean): If true, this program will shut down. You can use this to properly clean everything
    up before shutting the robot off.
    
    Configuration info:
    
    - `IP`: The IP address of the NetworkTables server. When connected to the RoboRIO, this should be set to
    `roboRIO-####-FRC.local` where #### is your team number.
    
    - `OutputTable`: The table to output data to. For most teams, this should be set to `SmartDashboard`.
    
    - `FlushOnUpdate`: If true, the client will flush all data immediately. This may reduce latency between the client
    and server.
    """
    ip = str()
    output_table = str()
    flush_on_update = bool()
    
    smart_dashboard = None
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.ip = component_config_root.find("IP").text
        self.output_table = component_config_root.find("OutputTable").text
        self.flush_on_update = component_config_root.find("FlushOnUpdate").text in \
            ['true', '1', 't', 'y', 'yes']
        
        logging.info("Connecting to {}...".format(self.ip))
        NetworkTables.initialize(server=self.ip)
        self.smart_dashboard = NetworkTables.getTable("SmartDashboard")
        while not NetworkTables.isConnected():
            logging.debug("waiting...")
            await asyncio.sleep(1)
        logging.debug("Connected!")
        self.smart_dashboard.putBoolean("vision_new_value", False)
        self.smart_dashboard.putNumber("vision_value", 0)
        self.smart_dashboard.putBoolean("vision_shutdown", False)

    # noinspection PyMethodMayBeStatic
    async def cleanup(self):
        NetworkTables.shutdown()
    
    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        if self.smart_dashboard.getBoolean("vision_shutdown", False):
            raise KeyboardInterrupt
        
        if len(data) != 0:
            self.smart_dashboard.putNumber("vision_value", data[0].angle)
            self.smart_dashboard.putBoolean("vision_new_value", True)
            if self.flush_on_update:
                NetworkTables.flush()
