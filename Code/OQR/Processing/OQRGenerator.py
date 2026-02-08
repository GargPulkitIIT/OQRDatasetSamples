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
    
    def develop_cdp_WB(self):
        pattern = np.ones([5, 5],dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                pattern[i][j]= 1
        pattern[0][-1] = 0
        pattern[1][-2] = 0
        pattern[1][-1] = 0
        pattern[2][2] = 0
        pattern[3][0] = 0
        pattern[4] = [1,0,0,0,0]
        return pattern

    def develop_cdp_BW(self):
        pattern = np.zeros([5, 5],dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                pattern[i][j]= 0
        pattern[0] = [1,0,1,1,1]
        pattern[1][1] = 1
        pattern[2][2] = 1
        pattern[3][3] = 1
        pattern[4][1] = 1
        pattern[4][3] = 1
        return pattern

    def change_cdp(self, img, pos_BW, pos_WB, scale, count= 5): #Here count is the no of occuerence of 2nd Optical Pattern
        # print("optical pattern", len(pos_BW), len(pos_WB))
        wb_option = random.sample(pos_WB, min(count, len(pos_WB)))
        bw_option = random.sample(pos_BW, min(count, len(pos_BW)))
        
        pattern_wb = np.repeat(np.repeat(self.develop_cdp_WB(), scale//5, axis=0), scale//5, axis=1)
        pattern_bw = np.repeat(np.repeat(self.develop_cdp_BW(), scale//5, axis=0), scale//5, axis=1)
        for i in wb_option:
            img[i[0]*scale:(i[0]+1)*scale, i[1]*scale:(i[1]+1)*scale] = pattern_wb
        for i in bw_option:
            img[i[0]*scale:(i[0]+1)*scale, i[1]*scale:(i[1]+1)*scale] = pattern_bw
        return img
    
    def merge_nf(self, nqr, fqr, scale = 50):
        # print(nqr)
        nqr_np = 1-np.array(nqr, dtype=int)
        fqr_np = 1-np.array(fqr, dtype=int)

        mismatch_coords = np.argwhere(nqr_np != fqr_np)
        scaled = np.repeat(np.repeat(fqr_np, scale, axis=0), scale, axis=1)

        hash_pattern = np.zeros((5, 5), dtype=int)
        hash_pattern[2, 1:4] = 1
        hash_pattern[1:4, 2] = 1
        # hash_pattern[2, 1:4] = 1
        # hash_pattern[1:4, 2] = 1


        #FarNear
        basic_cdp_wb = np.repeat(np.repeat(hash_pattern, scale//5, axis=0), scale//5, axis=1)
        basic_cdp_bw = 1- basic_cdp_wb
        
        #FarNear
        pos_bw = []
        pos_wb = []
        for i, j in mismatch_coords:
            if nqr_np[i, j] == 1: #white in near
                pos_bw.append((i,j))
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_bw
            else:
                pos_wb.append((i,j))
                scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_wb
        
        return self.change_cdp(scaled, pos_bw, pos_wb, scale)
    
    # def merge_nnf(self, nnqr, nqr, fqr, scale = 50):
    #     # print(nqr)
    #     nqr_np = 1-np.array(nqr, dtype=int)
    #     fqr_np = 1-np.array(fqr, dtype=int)

    #     mismatch_coords = np.argwhere(nqr_np != fqr_np)
    #     scaled = np.repeat(np.repeat(fqr_np, scale, axis=0), scale, axis=1)

    #     hash_pattern = np.zeros((5, 5), dtype=int)
    #     hash_pattern[1, :] = 1
    #     hash_pattern[3, :] = 1
    #     hash_pattern[:, 1] = 1 
    #     hash_pattern[:, 3] = 1 
    #     # hash_pattern[2, 1:4] = 1
    #     # hash_pattern[1:4, 2] = 1


    #     #FarNear
    #     basic_cdp_wb = np.repeat(np.repeat(hash_pattern, scale//5, axis=0), scale//5, axis=1)
    #     basic_cdp_bw = 1- basic_cdp_wb
        
    #     #FarNear
    #     pos_bw = []
    #     pos_wb = []
    #     for i, j in mismatch_coords:
    #         if nqr_np[i, j] == 1: #white in near
    #             pos_bw.append((i,j))
    #             scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_bw
    #         else:
    #             pos_wb.append((i,j))
    #             scaled[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = basic_cdp_wb
        
    #     return self.change_cdp(scaled, pos_bw, pos_wb, scale)
    
    def add_noise(self, img):
        mean = 0
        stddev = 20
        noise_1 = np.random.normal(mean, stddev, img.shape).astype(np.float32)
        noisy_img_1 = img.astype(np.float32) + noise_1
        noisy_img_1 = np.clip(noisy_img_1, 0, 255)  # Keep values valid

        return noisy_img_1.astype(np.uint8)

    def generateOQR(self, name, type, error, values, defaultMask=-1):     
        print("Generating OQR for ", name)
        qrs = []
        qrs_binary =[]
        qrs_image = []
        generated_version = None
        
        max_len = max(len(s) for s in values)
        values = [s.ljust(max_len) for s in values]
        
        for i, val in enumerate(values):
            qrs.append(self.qr_helper.generateTraditionalQR(val, None, self.ecc_mapping[error[i]]))
            qrs_binary.append(self.qr_helper.convertQRToBinary(qrs[-1]))
            # qrs_image.append(self.qr_helper.generateQRImage(qrs_binary[-1]))
            # print(self.qr_helper.determineQRVersion(qrs[-1]))
            if generated_version is None:
                generated_version = self.qr_helper.determineQRVersion(qrs[-1])
            else:
                if not generated_version == self.qr_helper.determineQRVersion(qrs[-1]):
                    print("Version Mismatch")
                    return "Version Mismatch"
        print("here")
        # qrFF = self.convertFarQR(qrs_binary[1])
        if type == "2":
            oqr_images = self.merge_nf(qrs_binary[0], qrs_binary[1], 50)
            
        if type == "3":
            oqr_images = self.merge_nf(qrs_binary[0], qrs_binary[1], 50)

        qrs_image.append(oqr_images*255)

        return qrs_image