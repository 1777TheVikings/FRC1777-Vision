# FRC Team 1777 Vision Code

This is team #1777 Viking's vision processing code framework. Unlike our previous years' vision
code, this code utilizes a framework designed to be reused, year after year. The code is divided
into three groups of components:

- Frame Generators: a single component that grabs images from some source to use for processing

    - `frame_generators/webcam.py`: Grabs frames from a webcam.
    
    - `frame_generators/video_file.py`: Grabs frames from a video file.

- Processor: a single component that performs the main bulk of the vision processing

    - `processors/contour.py`: HSV filtering => contour detection => bounding rects => non-maximum suppresion

- Post-Processors: any number of components that do extra stuff with the resulting images and
data

    - `postprocessors/display.py`: Outputs frames to the screen, optionally drawing the detected
objects on the screen.

    - `postprocessors/networktables.py`: Outputs data to a NetworkTables server.
    
    - `postprocessors/socketclient.py`: Outputs data to a socket server.
    
    - `postprocessors/record.py`: Records frames to a video file, optionally drawing the detected
objects on the video frames.

Every component has settings that can be configured in `config.xml` to change their normal
behavior. This file can be stored externally for easy editing on the field (e.g. on an SD card
inserted in the Jetson TX1's SD card slot). This file is also used to define which components
to use.

### "Why did you create this framework?"

1. This unconventional framework was designed to be used for many games, not just one. Rather
than remaking all of the vision code every year, programmers will only have to replace
individual components. Optimally, only the processing component will need to be replaced.

2. Programmers can develop, test, and share multiple components at once without conflicting with
other programmers' work. For example, if one programmer wants to refine the existing HSV +
contour detection method while another experiments with neural networks, their work will not
conflict on GitHub. Additionally, when testing on the robot, the only change that needs to be
made in order to switch between processing components is changing a single line in `config.xml`.

3. Features that are not always necessary can easily be toggled on and off in `config.xml`. For
example, grabbing frames from a video file is incredibly useful for standardized testing but
isn't helpful on the field. With this framework, programmers can easily switch between the two
by changing a single line in `config.xml`.

## Setup

This code was developed using Python 3.6.6 and OpenCV 3.4.0. However, you can *probably* go as
old as Python 3.4.0 and OpenCV 3.0.0 without any issues.

You will also need to install the following libraries:

- `numpy` is used for type hinting and is required to compile OpenCV from source with Python
bindings.

- `pynetworktables` is required to use the `networktables.py` postprocessor.

After all of the libraries are installed, clone this repository and use as described below. For
competition, configure your coprocessor to run `main.py` on startup.

## Usage

`python3 main.py [--config-file <path to config file>] [--log-file <path to log file>]`

`--config-file` is an optional parameter defining where to look for `config.xml`. It is
recommended not to store this directly on your team's coprocessor; instead, store it in
a removable storage device for easy configuring on the field.

`--log-file` is an optional parameter defining where to place the log file. Existing log files
with the same name will be overwritten.

## Configuration

All settings are stored in `config.xml`. This includes settings for the program as a whole and
for individual components. Below is a description of the settings used by the main program;
notes on each component's individual settings can be found in their source files.

- `FrameGenerator`: The name of the frame generator to use. Insert the name here that you
would use to import the file, not the full file name (e.g. `webcam` instead of `webcam.py`).
All frame generators should be located in `frame_generators/`.

- `Processor`: The name of the processor to use. The notes from `FrameGenerator` apply here. All
processors should be located in `processors/`.

- `PostProcessors`: A list of `PostProcessor` tags, where each `PostProcessor` tag specifies a
single postprocessor to use. The notes from `FrameGenerator` apply here. All postprocessors
should be located in `postprocessors/`.

- `IgnorePostProcessorLoadErrors`: If set to true, the program will continue to run if errors
are encountered when loading postprocessors (e.g. missing postprocessor file). It is not
recommended to use this; instead, disable the postprocessor that is causing the errors.

- `ComponentData`: A list of `Component` tags, where each `Component` tag specifies the settings
for each individual component. You don't need to delete any of these, since settings for unused
components are simply ignored. Each `Component` tag should have a `name` attribute corresponding
to the name of its component (notes from `FrameGenerator` apply here).
