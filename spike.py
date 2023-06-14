import cv2
import numpy as np
import pyautogui
import pytesseract


def get_value(top_left, top_right, bottom_left):
    """
    Belirtilen bölgedeki değerleri OCR (optik karakter tanıma) ile okuyarak döndürür.

    params:
    - top_left (tuple): Sol üst köşe koordinatları
    - top_right (tuple): Sağ üst köşe koordinatları
    - bottom_left (tuple): Sol alt köşe koordinatları

    returns:
    - result (str): OCR ile okunan değer
    """
    width = top_right[0] - top_left[0]  # Dikdörtgenin genişliği
    height = bottom_left[1] - top_left[1]  # Dikdörtgenin yüksekliği

    screenshot = pyautogui.screenshot(region=(top_left[0], top_left[1], width, height))  # Ekran görüntüsünü al

    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # OpenCV formatına dönüştür

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Gri tonlamalı görüntüye dönüştür

    inverted_image = cv2.bitwise_not(gray_image)  # Görüntüyü ters çevir (beyaz zemin üzerinde siyah yazı için)

    result = pytesseract.image_to_string(inverted_image)  # OCR ile oku
    if result == "SPIKE\n":
        return "KURULDU"
    else:
        return "KURULMADI"


def spike_status():
    """
    Spike durumunu kontrol eder ve döndürür.

    returns:
    - result (str): Spike durumu
    """
    top_left = (844, 146)  # Sol üst köşe koordinatları
    top_right = (914, 146)  # Sağ üst köşe koordinatları
    bottom_left = (844, 170)  # Sol alt köşe koordinatları
    result = get_value(top_left, top_right, bottom_left)
    return result
