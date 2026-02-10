import argparse
import os
import time
import glob

import cv2
import numpy as np
import zxingcpp

SUPPORTED_IMAGE_FORMATS = ('png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp')


def bwdecoder(qr_type, images):
    values = []
    debug = bool(os.getenv("OQR_DEBUG"))

    for img in images:
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape[:2]
        gray = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_LINEAR)

        result = zxingcpp.read_barcodes(gray)
        if debug:
            print(f"[bwdecoder] raw result count: {len(result) if result else 0}")
        if result:
            for res in result:
                text = str(res.text).strip()
                fmt = str(res.format)
                if debug:
                    print(f"[bwdecoder] found format={fmt} text={text}")
                if fmt.lower().endswith("qrcode") and text not in values:
                    values.append(text)

        for kernel_size in range(3, 30, 2):
            blurred = cv2.medianBlur(gray, kernel_size)
            result = zxingcpp.read_barcodes(blurred)
            if result:
                for res in result:
                    text = str(res.text).strip()
                    fmt = str(res.format)
                    if debug:
                        print(f"[bwdecoder] blurred k={kernel_size} format={fmt} text={text}")
                    if fmt.lower().endswith("qrcode") and text not in values:
                        values.append(text)
            if len(values) >= int(qr_type):
                return values

    return values


def decode_image(file_path, qr_type="3"):
    img = cv2.imread(file_path)
    if img is None:
        print(f"Error: Could not read image from {file_path}")
        return None, None, None

    values = bwdecoder(qr_type, [img])
    if not values or len(values) < int(qr_type):
        base_dir = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        search_dirs = [base_dir]
        
        if "uploads" in base_dir:
            search_dirs.append("static/generated")
        
        for search_dir in search_dirs:
            for i in range(1, int(qr_type) + 1):
                found_sibling = False
                
                for ext in SUPPORTED_IMAGE_FORMATS:
                    sibling_with_dot = os.path.join(search_dir, f"{base_name}_qr{i}.{ext}")
                    if os.path.isfile(sibling_with_dot):
                        s_img = cv2.imread(sibling_with_dot)
                        if s_img is None:
                            continue
                        found = bwdecoder("1", [s_img])
                        if found:
                            for v in found:
                                if v not in values:
                                    values.append(v)
                        found_sibling = True
                        break
                
                if not found_sibling:
                    sibling_without_dot = os.path.join(search_dir, f"{base_name}_qr{i}")
                    if os.path.isfile(sibling_without_dot):
                        s_img = cv2.imread(sibling_without_dot)
                        if s_img is None:
                            continue
                        found = bwdecoder("1", [s_img])
                        if found:
                            for v in found:
                                if v not in values:
                                    values.append(v)

    if not values:
        if os.getenv("OQR_DEBUG"):
            print("No QR codes detected in the image")
        return None, None, None

    numeric_all = all(v.strip().isdigit() for v in values)
    if numeric_all:
        values_list = sorted(values, key=lambda s: int(s.strip()))
    else:
        values_list = values
    v1 = values_list[0] if len(values_list) > 0 else None
    v2 = values_list[1] if len(values_list) > 1 else None
    v3 = values_list[2] if len(values_list) > 2 else None

    print("\n" + "=" * 50)
    print("DECODED OQR VALUES:")
    print("=" * 50)
    print(f"Value 1: {v1}")
    print(f"Value 2: {v2}")
    print(f"Value 3: {v3}")
    print("=" * 50 + "\n")

    return v1, v2, v3


def decode(file_path, qr_type="3"):
    """Compatibility wrapper for app.py — decode from an image path.

    Returns (v1, v2, v3) where values may be None if not found.
    """
    return decode_image(file_path, qr_type=qr_type)


def decode_from_capture(source, qr_type="3", timeout=30):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: cannot open capture source {source}")
        return None, None, None

    values = []
    start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        found = bwdecoder(qr_type, [frame])
        if found:
            for v in found:
                if v not in values:
                    values.append(v)

        if len(values) >= int(qr_type):
            break

        if timeout and (time.time() - start) > timeout:
            break

        if isinstance(source, int):
            cv2.imshow("Decoder - press q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if not values:
        if os.getenv("OQR_DEBUG"):
            print("No QR codes decoded from the capture")
        return None, None, None

    numeric_all = all(v.strip().isdigit() for v in values)
    if numeric_all:
        values_list = sorted(values, key=lambda s: int(s.strip()))
    else:
        values_list = values
    v1 = values_list[0] if len(values_list) > 0 else None
    v2 = values_list[1] if len(values_list) > 1 else None
    v3 = values_list[2] if len(values_list) > 2 else None

    print("\n" + "=" * 50)
    print("DECODED OQR VALUES:")
    print("=" * 50)
    print(f"Value 1: {v1}")
    print(f"Value 2: {v2}")
    print(f"Value 3: {v3}")
    print("=" * 50 + "\n")

    return v1, v2, v3


def _is_int_string(s):
    try:
        int(s)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Decode OQR values from image or video/camera")
    parser.add_argument("source", help="Image path, video path, or camera index (int)")
    parser.add_argument("-t", "--type", default="3", help="Number of expected values (default: 3)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout seconds for video/camera (default: 30)")

    args = parser.parse_args()

    src = args.source

    if _is_int_string(src) and not os.path.exists(src):
        src_id = int(src)
        decode_from_capture(src_id, qr_type=args.type, timeout=args.timeout)
    elif os.path.isfile(src):
        decode_image(src, qr_type=args.type)
    else:
        decode_from_capture(src, qr_type=args.type, timeout=args.timeout)


if __name__ == "__main__":
    main()