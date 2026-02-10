import os
import cv2
import csv
import random
import numpy as np

from Processing.qrcode import constants, main
from Processing.ImageModification import Modify_Image
from Processing.QRHelper import QR_Helper
from Processing.OQRGenerator import OQR_Generator
   

def folderGeneration(direcs):
    for direc in direcs:
        os.makedirs(direc, exist_ok=True)
            
def readValues(fileName):
    f = open(fileName, "r")
    data = f.readlines()
    data = [x.rstrip('\n') for x in data]
    return data

def generateOQR(name, type, data3, data2, data1=None):
    fn_error = "H"
    n_error = "H"
    f_error = "L"
    oqr_generator = OQR_Generator()
    
    if type == "2":
        result = oqr_generator.generateOQR(name, type, [n_error, f_error], [data2, data3])
    elif type == "3":
        result = oqr_generator.generateOQR(name, type, [fn_error, n_error, f_error], [data1, data2, data3])
    else:
        return "Invalid Type"
    
    if result != None:
        color_img = np.array(result[0]).astype(np.uint8)
        color_img = cv2.cvtColor(color_img, cv2.COLOR_GRAY2BGR)

        cv2.imwrite(name+".png", color_img)
        
        
generateOQR("Test3", "3", "3", "2", "1")
        
generateOQR("Test2", "2", "B", "A")