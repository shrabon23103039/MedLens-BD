import cv2
import numpy as np
from PIL import Image
import io
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import verify_barcode


def scan_barcode(image_bytes):
    try:
        # Convert bytes to OpenCV image
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Use OpenCV QR detector
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)

        if data:
            return data

        # Try barcode detector for 1D barcodes
        barcode_detector = cv2.barcode.BarcodeDetector()
        ok, decoded_info, _, _ = barcode_detector.detectAndDecodeWithType(img)

        if ok and decoded_info:
            return decoded_info[0]

        return None

    except Exception as e:
        print(f"Barcode scan error: {e}")
        return None


def check_medicine(image_bytes):
    barcode = scan_barcode(image_bytes)

    if not barcode:
        return {
            "status": "no_barcode",
            "barcode": None,
            "message_en": "No barcode found. Try a clearer photo.",
            "message_bn": "ছবিতে কোনো বারকোড পাওয়া যায়নি। স্পষ্ট ছবি তুলুন।"
        }

    result = verify_barcode(barcode)
    result["barcode"] = barcode
    return result


if __name__ == "__main__":
    print("✅ Barcode module ready")
    print("Testing DB verification...")
    fake = verify_barcode("1234567890")
    print(f"Unknown barcode: {fake['message_en']}")