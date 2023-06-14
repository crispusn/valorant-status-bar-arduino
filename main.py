import time
import cv2
import numpy as np
import pyautogui
import pytesseract
import serial
from spike import spike_status

arduino = serial.Serial('COM14', 9600)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

screen_width, screen_height = pyautogui.size()

global_spike_status = "KURULMADI"
global_boom_counter = 0
spike_timer = 30
count = 0


def get_health():
    """
    Can çubuğunun koordinatlarını al ve hesapla.

    returns:
    - result (str): Can değeri
    """
    top_left = (574, 1005)
    top_right = (651, 1005)
    bottom_left = (574, 1048)
    result = get_value(top_left, top_right, bottom_left)
    return result


def get_armor():
    """
    Zırh çubuğunun koordinatlarını al ve hesapla.

    returns:
    - result (str): Zırh değeri
    """
    top_left = (541, 1017)
    top_right = (566, 1017)
    bottom_left = (541, 1035)
    result = get_value(top_left, top_right, bottom_left)
    return result


def get_value(top_left, top_right, bottom_left):
    """
    Belirtilen bölgedeki değerleri OCR ile oku.

    params:
    - top_left (tuple): Sol üst köşe koordinatları
    - top_right (tuple): Sağ üst köşe koordinatları
    - bottom_left (tuple): Sol alt köşe koordinatları

    returns:
    - result (str): OCR ile okunan değer
    """
    width = top_right[0] - top_left[0]
    height = bottom_left[1] - top_left[1]

    screenshot = pyautogui.screenshot(region=(top_left[0], top_left[1], width, height))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)

    result = pytesseract.image_to_string(inverted_image,
                                         config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    if result == '':
        return "0"
    else:
        return result


def send_to_lcd(message):
    """
    Arduino'ya mesaj gönderme işlevi.

    params:
    - message (str): Gönderilecek mesaj
    """
    arduino.write(message.encode())


def get_spike_time(timer):
    """
    Spike için zamanlayıcı ayarla ve döndür.

    params:
    - timer (int): Spike zamanlayıcısı

    returns:
    - spike_timer (int/str): Spike zamanlayıcısı değeri
    """
    global spike_timer

    if (spike_timer == "BOOOM" or spike_timer - 1 <= 0):
        spike_timer = "BOOOM"
        global global_boom_counter
        global global_spike_status
        global_boom_counter += 1
    else:
        spike_timer = spike_timer - 1

    if (global_boom_counter >= 5):
        spike_timer = 30
        global_spike_status = "KURULMADI"
        global_boom_counter = 0

    return spike_timer


def check_global_spike_status():
    """
    Spike'in anlık durumunu kontrol etmek için kullanılan kod.

    returns:
    - spike_stat (str): Spike durumu
    """
    global global_spike_status

    if global_spike_status == "KURULDU":
        spike_stat = "KURULDU"
    else:
        spike_stat = "KURULMADI"

    return spike_stat


def update_lcd(spike_time, spike_stat):
    """
    Arduino'ya gönderilecek değerleri güncelleyen fonksiyon.

    params:
    - spike_time (int): Spike zamanlayıcısı
    - spike_stat (str): Spike durumu
    """
    health = get_health()
    armor = get_armor()
    can = int(health)
    zirh = int(armor)
    is_planted = spike_status()

    if (spike_stat == "KURULDU") or (is_planted == "KURULDU"):
        global global_spike_status, spike_timer
        global_spike_status = "KURULDU"
        spike_stat = "KURULDU"
        is_planted = get_spike_time(spike_time)

    message = "Can: {0}    Zirh: {1}   Spike {2}  ".format(can, zirh, is_planted)

    print(message)
    send_to_lcd(message)


while True:
    time.sleep(0.75)

    spike_stat = check_global_spike_status()
    print("main global spike status check", spike_stat)
    update_lcd(spike_timer, spike_stat)

    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').rstrip()
        if line == "STOP py":
            exit()
