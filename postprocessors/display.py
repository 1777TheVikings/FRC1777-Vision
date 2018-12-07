from typing import Any, NoReturn, List
from numpy import ndarray
import xml.etree.ElementTree as ElementTree
import cv2

from base_classes import PostProcessorBase


class DisplayPostProcessor(PostProcessorBase):
    """
    Outputs frames to the screen, optionally drawing the detected objects on the screen.
    
    Configuration info:
    
    - `Annotate`: If set to true, the location of detected objects will be drawn onto each frame.
    """
    
    annotate = bool()
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.annotate = component_config_root.find("Annotate").text in \
                        ['true', '1', 't', 'y', 'yes']
    
    async def cleanup(self):
        pass
    
    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        output_frame = frame
        if self.annotate:
            for i in data:
                cv2.rectangle(frame, (i.rect[0], i.rect[1]), (i.rect[2], i.rect[3]), (0, 255, 0), 2)
                cv2.putText(frame, str(i.angle), (int(i.x), int(i.y)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
        
        cv2.imshow("display", output_frame)
        cv2.waitKey(1)
