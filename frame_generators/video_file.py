from numpy import ndarray
import cv2
import xml.etree.ElementTree as ElementTree

from base_classes import FrameGeneratorBase


class VideoFileFrameGenerator(FrameGeneratorBase):
    """
    Grabs frames from a video file.
    
    Configuration info:
    
    - `FileName`: The path to the video file to read.
    
    - `ForceOutputSize`: If set to true, frames are resized to the size specified by `ForceOutputWidth` and
    `ForceOutputHeight`.
    
    - `ForceOutputWidth`: If `ForceOutputSize` is set to true, frames are resized to this width.
    
    - `ForceOutputHeight`: If `ForceOutputHeight` is set to true, frames are resized to this height.
    """
    
    file_name = str()
    force_output_size = bool()
    forced_output_width = int()
    forced_output_height = int()
    cap = None
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.file_name = component_config_root.find("FileName").text
        self.force_output_size = component_config_root.find("ForceOutputSize").text in \
            ['true', '1', 't', 'y', 'yes']
        if self.force_output_size:
            self.forced_output_width = int(component_config_root.find("ForcedOutputWidth").text)
            self.forced_output_height = int(component_config_root.find("ForcedOutputHeight").text)
        
        self.cap = cv2.VideoCapture(self.file_name)
    
    async def cleanup(self):
        self.cap.release()
    
    def get_frame(self) -> ndarray:
        rval, frame = self.cap.read()
        if not rval:
            raise FrameGeneratorBase.RvalException()
        
        if self.force_output_size:
            frame = cv2.resize(frame, (self.forced_output_width, self.forced_output_height))
        
        return frame
