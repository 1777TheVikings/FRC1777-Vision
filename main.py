import logging
import argparse
import signal
import asyncio
import collections
import time

from base_classes import *
import configuration_manager


COMPONENTS = dict()


async def load_components(config_file_name: str) -> NoReturn:
    global COMPONENTS
    COMPONENTS = await configuration_manager.ConfigurationManager(config_file_name).load_all_components()


async def main_loop(frame_generator_cmp: FrameGeneratorBase, processor_cmp: ProcessorBase,
                    postprocessor_cmps: List[PostProcessorBase]):
    while True:
        try:
            frame = frame_generator_cmp.get_frame()
            if frame is None:
                return
        except FrameGeneratorBase.RvalException:
            return
        
        data = processor_cmp.process(frame)
        
        for postprocessor_cmp in postprocessor_cmps:
            await postprocessor_cmp.postprocess(data, frame)


# noinspection PyShadowingNames
def signal_handler(sig, _) -> NoReturn:
    logging.info("Received signal {}, running cleanup functions".format(sig))
    asyncio.get_event_loop().stop()
    cleanup_loop = asyncio.new_event_loop()
    cleanup_loop.run_until_complete(call_cleanup_functions())


async def call_cleanup_functions() -> NoReturn:
    # taken from https://stackoverflow.com/a/2158532
    def flatten(l):
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
                yield from flatten(el)
            else:
                yield el
    
    for cmp in flatten(COMPONENTS.values()):
        logging.debug("Cleaning up component " + type(cmp).__name__)
        await cmp.cleanup()
        logging.debug("Finished cleaning up component " + type(cmp).__name__)


if __name__ == "__main__":
    config_file = "config.xml"
    log_file = "output.log"
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", help="use the specified config file", type=str)
    parser.add_argument("--log_file", help="log to the specified file", type=str)
    
    args = parser.parse_args()
    if args.config_file:
        config_file = args.config_file
    if args.log_file:
        log_file = args.log_file
    
    logging.basicConfig(filename=log_file, filemode="w", level=logging.DEBUG)
    
    load_components_loop = asyncio.new_event_loop()
    load_components_loop.run_until_complete(load_components(config_file))
    load_components_loop.close()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        main_async_loop = asyncio.new_event_loop()
        main_async_loop.run_until_complete(
            main_loop(COMPONENTS["FRAME_GENERATOR"], COMPONENTS["PROCESSOR"], COMPONENTS["POSTPROCESSORS"])
        )
        main_async_loop.close()
    except Exception as e:
    	logging.error(e)
    	main_async_loop.stop()
    	raise
    finally:
        cleanup_loop = asyncio.new_event_loop()
        cleanup_loop.run_until_complete(call_cleanup_functions())
