"""
Image format utility module for OQR encoder/decoder.
Provides format validation, conversion, and configuration.
"""

import cv2
import numpy as np

# Supported image formats with their file extensions
SUPPORTED_FORMATS = {
    'png': {
        'extension': '.png',
        'description': 'PNG (Portable Network Graphics)',
        'quality_param': cv2.IMWRITE_PNG_COMPRESSION,
        'quality_value': 9,
        'supports_transparency': True,
        'color_space': 'BGR'
    },
    'jpg': {
        'extension': '.jpg',
        'description': 'JPG (Joint Photographic Experts Group)',
        'quality_param': cv2.IMWRITE_JPEG_QUALITY,
        'quality_value': 95,
        'supports_transparency': False,
        'color_space': 'BGR'
    },
    'jpeg': {
        'extension': '.jpeg',
        'description': 'JPEG (Joint Photographic Experts Group)',
        'quality_param': cv2.IMWRITE_JPEG_QUALITY,
        'quality_value': 95,
        'supports_transparency': False,
        'color_space': 'BGR'
    },
    'bmp': {
        'extension': '.bmp',
        'description': 'BMP (Bitmap)',
        'quality_param': None,
        'quality_value': None,
        'supports_transparency': False,
        'color_space': 'BGR'
    },
    'tiff': {
        'extension': '.tiff',
        'description': 'TIFF (Tagged Image File Format)',
        'quality_param': cv2.IMWRITE_TIFF_COMPRESSION,
        'quality_value': 1,
        'supports_transparency': True,
        'color_space': 'BGR'
    },
    'tif': {
        'extension': '.tif',
        'description': 'TIF (Tagged Image File Format)',
        'quality_param': cv2.IMWRITE_TIFF_COMPRESSION,
        'quality_value': 1,
        'supports_transparency': True,
        'color_space': 'BGR'
    },
    'webp': {
        'extension': '.webp',
        'description': 'WEBP (WebP Image Format)',
        'quality_param': cv2.IMWRITE_WEBP_QUALITY,
        'quality_value': 95,
        'supports_transparency': True,
        'color_space': 'BGR'
    }
}


def validate_format(format_str):
    """
    Validate if the format is supported.
    
    Args:
        format_str: Format string (e.g., 'png', 'jpg', '.jpeg')
    
    Returns:
        bool: True if format is supported, False otherwise
    """
    format_clean = format_str.lower().strip('.')
    return format_clean in SUPPORTED_FORMATS


def get_image_extension(format_str):
    """
    Get the proper file extension for the given format.
    
    Args:
        format_str: Format string (e.g., 'png', 'jpg', '.jpeg')
    
    Returns:
        str: Extension with dot (e.g., '.png', '.jpg')
    """
    format_clean = format_str.lower().strip('.')
    if format_clean in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[format_clean]['extension']
    return '.png'  # Default fallback


def get_format_info(format_str):
    """
    Get detailed information about a format.
    
    Args:
        format_str: Format string (e.g., 'png', 'jpg', '.jpeg')
    
    Returns:
        dict: Format information or None if not supported
    """
    format_clean = format_str.lower().strip('.')
    return SUPPORTED_FORMATS.get(format_clean)


def get_save_parameters(format_str):
    """
    Get OpenCV save parameters for the specified format.
    
    Args:
        format_str: Format string (e.g., 'png', 'jpg', '.jpeg')
    
    Returns:
        list: OpenCV imwrite parameters or empty list
    """
    format_info = get_format_info(format_str)
    if format_info and format_info['quality_param'] is not None:
        return [format_info['quality_param'], format_info['quality_value']]
    return []


def convert_image_for_format(image_data, target_format):
    """
    Convert image data to be compatible with the target format.
    Handles color space conversion and format-specific requirements.
    
    Args:
        image_data: numpy array of image
        target_format: target format string (e.g., 'png', 'jpg', 'jpeg')
    
    Returns:
        tuple: (processed_image, save_params)
    """
    format_info = get_format_info(target_format)
    
    if not format_info:
        # Fallback to PNG if unsupported format
        return image_data, get_save_parameters('png')
    
    # Make a copy to avoid modifying original
    processed_img = image_data.copy()
    
    # Handle formats that don't support transparency (JPEG, BMP)
    if not format_info['supports_transparency']:
        if len(processed_img.shape) == 3 and processed_img.shape[2] == 4:
            # Convert BGRA to BGR
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGRA2BGR)
    
    save_params = get_save_parameters(target_format)
    return processed_img, save_params


def list_supported_formats():
    """
    Get list of all supported formats with descriptions.
    
    Returns:
        dict: Format names as keys, descriptions as values
    """
    return {fmt: info['description'] for fmt, info in SUPPORTED_FORMATS.items()}


def get_supported_format_list():
    """
    Get comma-separated list of supported formats.
    
    Returns:
        str: Comma-separated format names
    """
    return ', '.join(sorted(SUPPORTED_FORMATS.keys()))
