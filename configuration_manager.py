from base_classes import Component
from typing import Dict, Union, List, NoReturn
import xml.etree.ElementTree as ElementTree
import importlib
import inspect
import logging


class ComponentLoadError(Exception):
    def __init__(self, msg: str):
        super(ComponentLoadError, self).__init__(self, msg)


class ComponentConfigureError(Exception):
    def __init__(self, msg: str):
        super(ComponentConfigureError, self).__init__(self, msg)


class ConfigurationManager:
    def __init__(self, config_file_name: str):
        self.config_tree = ElementTree.parse(config_file_name)
        self.config_root = self.config_tree.getroot()

    async def load_all_components(self) -> Dict[str, Union[Component, List[Component]]]:
        out = dict()

        frame_generator_module_name = self.config_root.find("FrameGenerator").text
        out["FRAME_GENERATOR"] = await self.load_component("frame_generators." + frame_generator_module_name)

        processor_module_name = self.config_root.find("Processor").text
        out["PROCESSOR"] = await self.load_component("processors." + processor_module_name)

        postprocessor_root = self.config_tree.find("PostProcessors")
        postprocessor_module_names = [element.text for element in postprocessor_root.findall("PostProcessor")]
        out["POSTPROCESSORS"] = list()
        for name in postprocessor_module_names:
            out["POSTPROCESSORS"].append(await self.load_component("postprocessors." + name))

        return out

    async def load_component(self, module_name: str) -> Component:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise ComponentLoadError(module_name)  # ImportError
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and inspect.getmro(obj)[2] == Component:
                component = obj()
                await self.setup_component(component, module_name.split(".")[1])
                return component
        # no components found in file
        raise ComponentLoadError("No component class found in " + module_name)

    async def setup_component(self, obj: Component, name: str) -> NoReturn:
        for element in self.config_root.find("ComponentData").findall("Component"):
            if element.attrib.get("name") == name:
                logging.debug("Setting up component " + name)
                await obj.setup(element)
                logging.debug("Setup for component {} complete".format(name))
                return
        # no configuration found
        raise ComponentConfigureError("Missing configuration for " + obj.__class__.__name__)
