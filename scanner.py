from typing import List

import cv2
from pyzbar.pyzbar import decode, ZBarSymbol


def get_frame(device: int) -> any:  # does not work to do it this way. too slow
    stream = cv2.VideoCapture(device)
    _ = stream.read()  # must read 2 frames because first frame is always blank
    _, frame = stream.read()
    return frame


def decode_barcode(img) -> List[bytes]:
    detected_barcodes = decode(img, symbols=[ZBarSymbol.EAN13])
    if not detected_barcodes:
        return []
    else:
        return [x.data for x in detected_barcodes]
