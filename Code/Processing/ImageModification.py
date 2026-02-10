import os
import cv2
import csv
import random
import numpy as np

import svgwrite
import cairosvg
from PIL import Image
import xml.etree.ElementTree as ET


class Modify_Image:
    def __init__(self):
        pass
    
    def scaleImg(self, img, scale):
        return np.repeat(np.repeat(img, scale, axis=0), scale, axis=1)
    
    def convertToSVG(self, pngFile, svgFile):
        img = Image.open(pngFile).convert("RGB")
        arr = np.array(img)
        h, w, _ = arr.shape

        visited = np.zeros((h, w), dtype=bool)
        dwg = svgwrite.Drawing(svgFile, profile="tiny", size=(w, h), fill="white")

        for y in range(h):
            for x in range(w):
                if visited[y, x]:
                    continue

                base_color = tuple(arr[y, x])
                max_size = min(h - y, w - x)
                square_size = 1
                while square_size <= max_size:
                    region = arr[y:y+square_size, x:x+square_size]
                    if region.shape[0] != square_size or region.shape[1] != square_size:
                        break
                    if not np.all(region == region[0, 0]):
                        break
                    square_size += 1

                square_size -= 1 

                if square_size > 0:
                    visited[y:y+square_size, x:x+square_size] = True
                    rgb = f"rgb{base_color}"
                    dwg.add(dwg.rect(
                        insert=(x, y),
                        size=(square_size, square_size),
                        fill=rgb,
                        stroke=rgb,
                        stroke_width=0
                    ))

        dwg.save()
    
    def convertToEPS(self, svgFile, epsFile):
        cairosvg.svg2eps(url=svgFile, write_to=epsFile)
        
    def convertToPDF(self, svgFile, pdfFile):
        cairosvg.svg2pdf(url=svgFile, write_to=pdfFile)
    
    def tiltPNG(self, img, offset=0.028):
        offset = offset*img.shape[0]
        
        pt1 = np.float32([[0,0],[img.shape[0],0],[0,img.shape[1]],[img.shape[0], img.shape[1]]])
        pt2 = np.float32([[0+offset,0],[img.shape[0]-offset,0],[0,img.shape[1]],[img.shape[0], img.shape[1]]])
        
        M = cv2.getPerspectiveTransform(pt1,pt2)
 
        white_image = np.zeros((img.shape[0],img.shape[1], 3), np.uint8)
        white_image[:,:,:] = 255
        dst = cv2.warpPerspective(img,M,(img.shape[0],img.shape[1]), white_image, borderMode=cv2.BORDER_TRANSPARENT)
        
        return dst
    
    def get_perspective_transform_matrix(self, src_pts, dst_pts):
        src_pts = np.array(src_pts, dtype=np.float32)
        dst_pts = np.array(dst_pts, dtype=np.float32)
        
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return matrix.tolist()

    def apply_perspective_to_point(self, matrix, point):
        point = np.array([point[0], point[1], 1.0])  # Make it a homogeneous coordinate
        transformed_point = np.dot(matrix, point)  # Apply matrix
        transformed_point = transformed_point / transformed_point[2]  # Normalize to x, y
        return transformed_point[0], transformed_point[1]
    
    def tiltSVG(self, svg_file, output_file, img_size=1250):

        dst_pts = [[0+35, 0], [img_size-35, 0], [0, img_size], [img_size, img_size]]
        src_pts = [[0, 0], [img_size, 0], [0, img_size], [img_size, img_size]]
        
        transform_matrix = self.get_perspective_transform_matrix(src_pts, dst_pts)
    
        tree = ET.parse(svg_file)
        root = tree.getroot()
        svg_ns = "{http://www.w3.org/2000/svg}"
        
        for rect in root.findall(f".//{svg_ns}rect"):
            x = float(rect.attrib["x"])
            y = float(rect.attrib["y"])
            w = float(rect.attrib["width"])
            h = float(rect.attrib["height"])
            fill = rect.attrib.get("fill", "black")
            
            corners = [
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h)
            ]
            transformed_corners = [self.apply_perspective_to_point(transform_matrix, pt) for pt in corners]
            points_str = " ".join(f"{px},{py}" for px, py in transformed_corners)

            polygon = ET.Element(f"{svg_ns}polygon", {
                "points": points_str,
                "fill": fill,
                "stroke": fill,
                "stroke-width": "0"
            })

            parent = rect.getparent() if hasattr(rect, 'getparent') else root
            parent.remove(rect)
            parent.append(polygon)


        tree.write(output_file)
