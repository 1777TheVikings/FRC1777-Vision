from abc import ABC, abstractmethod
from typing import Any, List, NoReturn
from numpy import ndarray
import xml.etree.ElementTree as ElementTree


class Component(ABC):
    """ Components are self-contained classes that perform a certain function in
        the pipeline. These can be switched around and configured in config.xml.
    """
    @abstractmethod
    async def setup(self, component_config_root: ElementTree.Element) -> NoReturn:
        """ Executed before the main loop begins. Use this to initialize variables
            based on configuration data.

            Arguments:
            - component_config_root: Base ET element for the component. Contains
              various configuration data.
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> NoReturn:
        """ Executed after the main loop ends. Use this to close resources that
            cannot be left open (e.g sockets, files).
        """
        pass


class FrameGeneratorBase(Component):
    """ Frame generators retrieve frames from an arbitrary source. These are the
        first steps in the path and therefore have no inputs.
    """
    @abstractmethod
    def get_frame(self) -> ndarray:
        """ Retrieve a single frame from the generator.

            Returns a frame.
        """
        pass

    class RvalException(Exception):
        """ Raised when the frame generator cannot be created.
        """
        pass


class FrameData:
    """ This class provides a standardized format for processor component output
        data. It also automatically calculates helpful values.
    """
    def __init__(self, rect: ndarray, frame_width: int = 640):
        """ Arguments:
            - rect: An array describing a rectangle circumscribing a detected
              object. Should be in the format [x1, y1, x2, y2].
            - frame_width: The width of the frames generated by the active
              FrameGenerator component. Defaults to 640px.
        """
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
    """ Processors take in frames from a FrameGenerator and output zero
        or more detected objects (FrameData).
    """
    @abstractmethod
    def process(self, frame: ndarray) -> List[FrameData]:
        """ Process a single frame and retrieve the locations of objects.

            Arguments:
            - frame: The input image to process

            Returns a list of FrameData objects, each of which corresponds to
            a detected object.
        """
        pass


class PostProcessorBase(Component):
    """ Postprocessors take in a list of DataFrames (which may be empty)
        and a frame. Unlike the other Component types, multiple Postprocessors
        can be used at the same time.They can do anything with the data received,
        but they cannot modify what another Postprocessor receives.

        All Postprocessors run asynchronously for two reasons:
        1.) Postprocessors usually rely on blocking I/O operations
        2.) Postprocessors do not depend on data from other Postprocessors
    """
    @abstractmethod
    async def postprocess(self, data: List[Any], frame: ndarray) -> NoReturn:
        """ Perform any operation on the detected objects and video frame.

            Arguments:
            - data: A list of DataFrames, which may be empty.
            - frame: The input image
        """
        pass
