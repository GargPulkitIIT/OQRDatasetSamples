import os
import cv2
import csv
import random
import numpy as np

from Processing.qrcode import constants, main

class QR_Helper:
    def __init__(self):
        pass
    
    def generateTraditionalQR(self, value, version, error, mask=-1, borderSize = 0):
        if mask!=-1:
            qr = main.QRCode(version = version, error_correction=error, border = borderSize, mask_pattern = mask)
        else:
            qr = main.QRCode(version = version, error_correction=error, border = borderSize)
        qr.add_data(value)
        return qr
    
    def determineQRVersion(self, qr):
        return (len(qr.get_matrix())-17)//4
    
    def convertQRToBinary(self, qr):
        mat = np.array(qr.get_matrix())
        mat = mat*1
        mat = [''.join(map(str, mat[i].tolist())) for i in range(mat.shape[0])]
        mat = [list(map(int,list(x))) for x in mat]
        return mat
    
    def generateQRImage(self, qr_text):
        img = np.zeros([len(qr_text), len(qr_text[0]), 3],dtype=np.uint8)
        for i in range(len(qr_text)):
            for j in range(len(qr_text[0])):
                    if qr_text[i][j] == 0:
                        img[i][j] = [255, 255, 255]
        return img