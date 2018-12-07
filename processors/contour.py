from typing import List
import numpy
import cv2
import xml.etree.ElementTree as ElementTree

from base_classes import ProcessorBase, FrameData


class ContourProcessor(ProcessorBase):
    """
    HSV filtering => contour detection => bounding rects => non-maximum suppresion
    
    Configuration info:
    
    - `HueRange`: A range from 0-255 specifying the minimum and maximum hue for HSV filtering (format: `<min>-<max>`).
    
    - `LuminanceRange`: A range from 0-255 specifying the minimum and maximum luminance for HSV filtering (format:
    `<min>-<max>`).
    
    - `SaturationRange`: A range from 0-255 specifying the minimum and maximum saturation for HSV filtering (format:
    `<min>-<max>`).
    
    - `WidthRange`: A range specifying the minimum and maximum width for contour filtering (format: `<min>-<max>`).
    
    - `HeightRange`: A range specifying the minimum and maximum height for contour filtering (format: `<min>-<max>`).
    
    - `AreaRange`: A range specifying the minimum and maximum width for contour filtering (format: `<min>-<max>`).
    
    - `OverlapThreshold`: A float in the range 0-1 specifying the minimum necessary percentage of overlap between
    rectangles before the non-maximum suppression algorithm combines them. Higher values will require more of an
    overlap, while lower values will merge rectangles more aggressively. 0.3-0.5 are recommended.
    """
    hueRange = (int(), int())
    luminanceRange = (int(), int())
    saturationRange = (int(), int())
    widthRange = (int(), int())
    heightRange = (int(), int())
    areaRange = (int(), int())
    overlapThreshold = float()
    
    async def setup(self, component_config_root: ElementTree.Element):
        self.hueRange = tuple([int(i) for i in component_config_root.find("HueRange").text.split('-')])
        self.luminanceRange = tuple([int(i) for i in component_config_root.find("LuminanceRange").text.split('-')])
        self.saturationRange = tuple([int(i) for i in component_config_root.find("SaturationRange").text.split('-')])
        self.widthRange = tuple([int(i) for i in component_config_root.find("WidthRange").text.split('-')])
        self.heightRange = tuple([int(i) for i in component_config_root.find("HeightRange").text.split('-')])
        self.areaRange = tuple([int(i) for i in component_config_root.find("AreaRange").text.split('-')])
    
    async def cleanup(self):
        pass
    
    def process(self, frame: numpy.ndarray) -> List[FrameData]:
        blurred = cv2.blur(frame, (15, 15))
    
        hsl_filtered = cv2.inRange(cv2.cvtColor(blurred, cv2.COLOR_BGR2HLS),
                                   (self.hueRange[0], self.luminanceRange[0], self.saturationRange[0]),
                                   (self.hueRange[1], self.luminanceRange[1], self.saturationRange[1]))
    
        eroded = cv2.erode(hsl_filtered, None, (-1, -1), iterations=5, borderType=cv2.BORDER_CONSTANT, borderValue=(-1))
        dilated = cv2.dilate(eroded, None, (-1, -1), iterations=5, borderType=cv2.BORDER_CONSTANT,
                             borderValue=(-1))
    
        contour_image, contours, hierarchy = cv2.findContours(dilated, mode=cv2.RETR_EXTERNAL,
                                                              method=cv2.CHAIN_APPROX_SIMPLE)
    
        contours_hulls = []
        for i in contours:
            contours_hulls.append(cv2.convexHull(i))
        contours_filtered = self.filter_contours(contours_hulls)
        
        rects = [cv2.boundingRect(i) for i in contours_filtered]
        # converting coordinate format + using numpy arrays for better performance
        rects = numpy.array([(i[0], i[1], i[0] + i[2], i[1] + i[3]) for i in rects])
        rects = self.non_max_suppression(rects, self.overlapThreshold)

        return [FrameData(rect, frame.shape[1]) for rect in rects]

    def filter_contours(self, contours: List[numpy.ndarray]) -> List[numpy.ndarray]:
        output = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < self.widthRange[0] or w > self.widthRange[1]:  # min/max width
                continue
            if h < self.heightRange[0] or h > self.heightRange[1]:  # min/max height
                continue
        
            area = cv2.contourArea(contour)
            if area < self.areaRange[0] or area > self.areaRange[1]:  # min/max area
                continue
        
            output.append(contour)
    
        return output
    
    # based off of https://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
    @staticmethod
    def non_max_suppression(rects: numpy.array, overlap_thresh: float) -> numpy.array:
        if len(rects) == 0:
            return []
        
        if rects.dtype.kind == "i":
            rects = rects.astype("float")
        
        pick = []
        
        x1 = rects[:, 0]
        y1 = rects[:, 1]
        x2 = rects[:, 2]
        y2 = rects[:, 3]
        
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = numpy.argsort(y2)
        
        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            xx1 = numpy.maximum(x1[i], x1[idxs[:last]])
            yy1 = numpy.maximum(y1[i], y1[idxs[:last]])
            xx2 = numpy.maximum(x2[i], x2[idxs[:last]])
            yy2 = numpy.maximum(y2[i], y2[idxs[:last]])
            
            w = numpy.maximum(0, xx2 - xx1 + 1)
            h = numpy.maximum(0, yy2 - yy1 + 1)
            
            overlap = (w * h) / area[idxs[:last]]

            idxs = numpy.delete(idxs, numpy.concatenate(([last],
                                                         numpy.where(overlap > overlap_thresh)[0])))
        
        return rects[pick].astype("int")
