import os
import cv2
import csv
import random
import numpy as np

from Processing.qrcode import constants, main
from Processing.ImageModification import Modify_Image
from Processing.QRHelper import QR_Helper
from Processing.ValueGenerator import ValueGenerator

class OQR_Generator:
    
    qr_helper = QR_Helper()
    
    ecc_mapping =  {"L": constants.ERROR_CORRECT_L, "M": constants.ERROR_CORRECT_M, "Q": constants.ERROR_CORRECT_Q, "H": constants.ERROR_CORRECT_H}
    patterns = [[10,10,10,10,10], [5,15,10,15,5], [10, 7, 16, 7, 10], [7,10,16,10,7]]
    
    def __init__(self):
        pass
    
    def merge_nf(self, nqr, fqr, scale = 50):
        nqr_np = 1-np.array(nqr, dtype=int)
        fqr_np = 1-np.array(fqr, dtype=int)

        mismatch_coords = np.argwhere(nqr_np != fqr_np)
        scaled = np.repeat(np.repeat(fqr_np, scale, axis=0), scale, axis=1)

        optical_pattern = np.zeros((5, 5), dtype=int)
        optical_pattern[2, 1:4] = 1
        optical_pattern[1:4, 2] = 1

        #FarNear
        basic_cdp_wb = np.repeat(np.repeat(optical_pattern, scale//5, axis=0), scale//5, axis=1)
        basic_cdp_bw = 1- basic_cdp_wb

        for i, j in mismatch_coords:
            if nqr_np[i, j] == 1: 
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_wb
            else:
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_bw
        
        return scaled
    
    def merge_nnf(self, nnqr, nqr, fqr, scale = 150):

        nnqr_np = 1-np.array(nnqr, dtype=int)
        nqr_np = 1-np.array(nqr, dtype=int)
        fqr_np = 1-np.array(fqr, dtype=int)

        mismatch_coords_1 = np.argwhere(nnqr_np != nqr_np)
        mismatch_coords_2 = np.argwhere(nqr_np != fqr_np)
        scaled = np.repeat(np.repeat(fqr_np, scale, axis=0), scale, axis=1)

        
        optical_pattern = np.zeros((5, 5), dtype=int)
        optical_pattern[2, 1:4] = 1
        optical_pattern[1:4, 2] = 1

        basic_cdp_wb = np.repeat(np.repeat(optical_pattern, scale//5, axis=0), scale//5, axis=1)
        basic_cdp_bw = 1- basic_cdp_wb

        for i, j in mismatch_coords_2:
            if nqr_np[i, j] == 1: 
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_wb
            else:
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_bw
        

        for i, j in mismatch_coords_1:
            if nqr_np[i, j] == 1: 
                if fqr_np[i, j] == 1: 
                    scaled[i*scale+70:i*scale+80, j*scale+50:j*scale+100] = np.zeros((10, 50), dtype=int)
                else:
                    scaled[i*scale+70:i*scale+80, j*scale+60:j*scale+90] = np.zeros((10, 30), dtype=int)
                scaled[i*scale+50:i*scale+100, j*scale+70:j*scale+80] = np.zeros((50, 10), dtype=int)
            else:
                if fqr_np[i, j] == 1:
                    scaled[i*scale+70:i*scale+80, j*scale+60:j*scale+90] = 1-np.zeros((10, 30), dtype=int)
                else:
                    scaled[i*scale+70:i*scale+80, j*scale+50:j*scale+100] = 1-np.zeros((10, 50), dtype=int)
                scaled[i*scale+50:i*scale+100, j*scale+70:j*scale+80] = 1-np.zeros((50, 10), dtype=int)
        return scaled
    
    def add_noise(self, img):
        mean = 0
        stddev = 20
        noise_1 = np.random.normal(mean, stddev, img.shape).astype(np.float32)
        noisy_img_1 = img.astype(np.float32) + noise_1
        noisy_img_1 = np.clip(noisy_img_1, 0, 255) 

        return noisy_img_1.astype(np.uint8)
    
    def add_white_padding(self, img, padding_size=50):
        """
        Add white padding around the image on all sides
        
        Args:
            img: Input image (numpy array)
            padding_size: Size of padding in pixels (default: 50)
        
        Returns:
            Image with white padding added
        """
        height, width = img.shape[:2]
        
        if len(img.shape) == 2:  
            padded_img = np.ones((height + 2*padding_size, width + 2*padding_size), dtype=img.dtype) * 255
            padded_img[padding_size:padding_size+height, padding_size:padding_size+width] = img
        else:  
            padded_img = np.ones((height + 2*padding_size, width + 2*padding_size, img.shape[2]), dtype=img.dtype) * 255
            padded_img[padding_size:padding_size+height, padding_size:padding_size+width, :] = img
        
        return padded_img

    def generateOQR(self, name, type, error, values, defaultMask=-1, padding_size=50):     
        print("Generating OQR for ", name)
        qrs = []
        qrs_binary = []
        qrs_image = []
        generated_version = None
        
        values = [str(v) for v in values]
        
        max_len = max(len(s) for s in values)
        values = [s.ljust(max_len) for s in values]
        
        final_values = []
        for i, val in enumerate(values):
            qrs.append(self.qr_helper.generateTraditionalQR(val, None, self.ecc_mapping[error[i]]))
            qrs_binary.append(self.qr_helper.convertQRToBinary(qrs[-1]))
            
            if generated_version is None:
                generated_version = self.qr_helper.determineQRVersion(qrs[-1])
            else:
                while (not generated_version == self.qr_helper.determineQRVersion(qrs[-1])):
                    qrs_binary.pop()
                    qrs.pop()  
                    val += " "
                    qrs.append(self.qr_helper.generateTraditionalQR(val, None, self.ecc_mapping[error[i]]))
                    qrs_binary.append(self.qr_helper.convertQRToBinary(qrs[-1]))
                    
            final_values.append(val)

        oqr_images = None
        
        if type == "2":
            oqr_images = self.merge_nf(qrs_binary[0], qrs_binary[1], 50)
            
        if type == "3":
            oqr_images = self.merge_nnf(qrs_binary[0], qrs_binary[1], qrs_binary[2], 150)

        if oqr_images is not None:
            scaled_image = (oqr_images * 255).astype(np.uint8)
            
            padded_image = self.add_white_padding(scaled_image, padding_size=padding_size)
            
            qrs_image.append(padded_image)
            return qrs_image
        
        return None