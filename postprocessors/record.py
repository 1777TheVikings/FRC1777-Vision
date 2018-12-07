from typing import Any, NoReturn, List
from numpy import ndarray
import xml.etree.ElementTree as ElementTree
import cv2

from base_classes import PostProcessorBase


class RecordPostProcessor(PostProcessorBase):
    """
    Records frames to a video file.

    Configuration info:

    - `FileName`: The path to the video file to write to.

    - `ForceOutputSize`: If set to true, frames are resized to the size specified by `ForceOutputWidth` and
    `ForceOutputHeight`.

    - `ForceOutputWidth`: If `ForceOutputSize` is set to true, frames are resized to this width.

    - `ForceOutputHeight`: If `ForceOutputHeight` is set to true, frames are resized to this height.
    
    - `TargetFPS`: The frame rate to play video back at. It's recommended to set this to whatever number you used
    for the frame generator.

    - `Annotate`: If set to true, output rectangles will be drawn in the output video.
    """
    file_name = str()
    output_width = int()
    output_height = int()
    target_fps = int()
    annotate = bool()
    out = None
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.file_name = component_config_root.find("FileName").text
        self.output_width = int(component_config_root.find("ForcedOutputWidth").text)
        self.output_height = int(component_config_root.find("ForcedOutputHeight").text)
        self.target_fps = int(component_config_root.find("TargetFPS").text)
        self.annotate = component_config_root.find("Annotate").text in ['true', '1', 't', 'y', 'yes']
        
        self.out = cv2.VideoWriter(self.file_name, cv2.VideoWriter_fourcc(*"XVID"), self.target_fps,
                                   (self.output_width, self.output_height))
    
    async def cleanup(self):
        self.out.release()
    
    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        if self.annotate:
            for i in data:
                cv2.rectangle(frame, (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 2)

        self.out.write(frame)
