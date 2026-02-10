import os
import cv2
import csv
import random
import numpy as np

from Processing.qrcode import constants, main
from Processing.ImageModification import Modify_Image
from Processing.QRHelper import QR_Helper
from Processing.OQRGenerator import OQR_Generator

SUPPORTED_FORMATS = {
    'png': '.png',
    'jpg': '.jpg',
    'jpeg': '.jpeg',
    'bmp': '.bmp',
    'tiff': '.tiff',
    'tif': '.tif',
    'webp': '.webp'
}

def get_image_extension(format_str):
    """
    Get the proper file extension for the given format.
    Returns extension with dot (e.g., '.png', '.jpg')
    """
    format_lower = format_str.lower().strip('.')
    return SUPPORTED_FORMATS.get(format_lower, '.png')

def convert_image_format(image_data, target_format):
    """
    Ensure image can be saved in the target format.
    Handles color space conversion if needed for specific formats.
    
    Args:
        image_data: numpy array of image
        target_format: target format string (e.g., 'png', 'jpg', 'jpeg')
    
    Returns:
        Tuple of (processed_image, save_params)
    """
    target_format = target_format.lower().strip('.')
    
    if target_format in ('jpg', 'jpeg'):
        if len(image_data.shape) == 3 and image_data.shape[2] == 4:
            image_data = cv2.cvtColor(image_data, cv2.COLOR_BGRA2BGR)
        return image_data, [cv2.IMWRITE_JPEG_QUALITY, 95]
    
    elif target_format == 'png':
        return image_data, [cv2.IMWRITE_PNG_COMPRESSION, 9]
    
    elif target_format == 'bmp':
        if len(image_data.shape) == 3 and image_data.shape[2] == 4:
            image_data = cv2.cvtColor(image_data, cv2.COLOR_BGRA2BGR)
        return image_data, []
    
    elif target_format in ('tiff', 'tif'):
        return image_data, [cv2.IMWRITE_TIFF_COMPRESSION, 1]
    
    elif target_format == 'webp':
        return image_data, [cv2.IMWRITE_WEBP_QUALITY, 95]
    
    else:
        return image_data, [cv2.IMWRITE_PNG_COMPRESSION, 9]
   

def folderGeneration(direcs):
    for direc in direcs:
        os.makedirs(direc, exist_ok=True)
            
def readValues(fileName):
    with open(fileName, "r") as f:
        data = f.readlines()
    return [x.rstrip('\n') for x in data]


def generateOQR(name, type, data3, data2, data1=None, format='png'):
    """
    Generate OQR code and save in specified format.
    
    Args:
        name: Name for the generated QR code
        type: Type of QR code ("2" or "3")
        data3: Third data field
        data2: Second data field
        data1: First data field (optional, None for Type 2)
        format: Output format - 'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp' (default: 'png')
    
    Returns:
        Path to the generated QR code image, or None if generation failed
    """
    fn_error = "H"
    n_error = "H"
    f_error = "L"
    oqr_generator = OQR_Generator()
    
    if type == "2":
        result = oqr_generator.generateOQR(name, type, [n_error, f_error], [data2, data3])
    elif type == "3":
        result = oqr_generator.generateOQR(name, type, [fn_error, n_error, f_error], [data1, data2, data3])
    else:
        print("Invalid Type")
        return None
    
    if result is not None and len(result) > 0:
        color_img = np.array(result[0]).astype(np.uint8)
        color_img = cv2.cvtColor(color_img, cv2.COLOR_GRAY2BGR)
        
        os.makedirs("static/generated", exist_ok=True)
        
        file_ext = get_image_extension(format)
        output_path = f"static/generated/{name}{file_ext}"
        
        processed_img, save_params = convert_image_format(color_img, format)
        
        if save_params:
            cv2.imwrite(output_path, processed_img, save_params)
        else:
            cv2.imwrite(output_path, processed_img)
        print(f"OQR saved: {output_path} ({format.upper()})")
        
        try:
            qr_helper = QR_Helper()
            if type == "2":
                vals = [data2, data3]
            else:
                vals = [data1, data2, data3]
            
            for idx, val in enumerate(vals):
                if not val:
                    continue
                try:
                    qr = qr_helper.generateTraditionalQR(str(val), None, constants.ERROR_CORRECT_H)
                    mat = qr_helper.convertQRToBinary(qr)
                    qr_img = qr_helper.generateQRImage(mat).astype(np.uint8)
                    qr_path = f"static/generated/{name}_qr{idx+1}{file_ext}"
                    
                    processed_qr, qr_save_params = convert_image_format(qr_img, format)
                    if qr_save_params:
                        cv2.imwrite(qr_path, processed_qr, qr_save_params)
                    else:
                        cv2.imwrite(qr_path, processed_qr)
                    print(f"✓ Sibling QR saved: {qr_path} ({format.upper()})")
                except Exception as e:
                    print(f"✗ Failed to generate sibling QR {idx+1}: {e}")
        except Exception as e:
            print(f"✗ Failed to generate sibling QR files: {e}")
        
        return output_path
    else:
        print(f"✗ Failed to generate OQR: {name}")
        return None


def encode(name, type, data3, data2, data1=None, format='png'):
    if format.lower().strip('.') not in SUPPORTED_FORMATS:
        print(f"✗ Unsupported format: {format}. Supported: {', '.join(SUPPORTED_FORMATS.keys())}")
        format = 'png'
    
    return generateOQR(name, type, data3, data2, data1, format)


if __name__ == "__main__":
    print("Testing Type 3 OQR...")
    encode("Test3", "3", "3", "2", "1")
    
    print("\nTesting Type 2 OQR...")
    encode("Test2", "2", "B", "A")