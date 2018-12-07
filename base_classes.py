from abc import ABC, abstractmethod
from typing import Any, List, NoReturn
from numpy import ndarray
import xml.etree.ElementTree as ElementTree


class Component(ABC):
    @abstractmethod
    async def setup(self, component_config_root: ElementTree.Element):
        pass
    
    @abstractmethod
    async def cleanup(self):
        pass


class FrameGeneratorBase(Component):
    @abstractmethod
    def get_frame(self) -> ndarray:
        pass

    class RvalException(Exception):
        pass


class FrameData:
    def __init__(self, rect: ndarray, frame_width: int = 640):
        self.rect = rect  # format: [x1, y1, x2, y2]

        self.x = (rect[0] + rect[2]) / 2
        self.y = (rect[1] + rect[3]) / 2

        # TODO: Get 60 degree FOV value from frame generator
        # TODO: Perhaps also get the frame width from the frame generator as well?
        midway = frame_width / 2
        if self.x < midway:
            self.angle = (68.5 / frame_width) * (midway - self.x)
        else:
            self.angle = -1 * ((68.5 / frame_width) * (self.x - midway))


class ProcessorBase(Component):
    @abstractmethod
    def process(self, frame: ndarray) -> List[FrameData]:
        pass


class PostProcessorBase(Component):
    @abstractmethod
    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        pass
