from numpy import ndarray
import cv2
import xml.etree.ElementTree as ElementTree

from base_classes import FrameGeneratorBase


class WebcamFrameGenerator(FrameGeneratorBase):
    """
    Grabs frames from a webcam.
    
    Configuration info:
    
    - `CameraID`: The ID of the video camera to use. Normally, this should be "0".
    
    - `Width`: The desired width of each frame.
    
    - `Height`: The desired height of each frame.
    
    - `FPS`: The desired framerate to retrieve frames at.
    """
    camera_id = int()
    width = int()
    height = int()
    fps = int()
    cap = None
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.camera_id = int(component_config_root.find("CameraID").text)
        self.width = int(component_config_root.find("Width").text)
        self.height = int(component_config_root.find("Height").text)
        self.fps = int(component_config_root.find("FPS").text)
        
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)
        self.cap.set(5, self.fps)
    
    async def cleanup(self):
        self.cap.release()
    
    def get_frame(self) -> ndarray:
        rval, frame = self.cap.read()
        if not rval:
            raise FrameGeneratorBase.RvalException()
        
        return frame
