# -*- coding: utf-8 -*-
#
# Author: @billz
# Author URI: https://github.com/billz
# Description: RaspAP stats display for the Adafruit Mini PiTFT,
#   a 135x240 Color TFT add-on for the Raspberry Pi.
#   Based on Adafruit's rgb_display_ministats.py
# See: https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display
# License: MIT License

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz)
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image with mode 'RGB'
height = disp.width   # swap height/width to rotate it to landscape
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get a drawing object and clear the image
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image,rotation)

# Define some constants
padding = -2
top = padding
bottom = height-padding
text_y_offset = 5
x = 0

# Load FiraCode TTF Font
font_path = '/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf'
font_size = 24
font = ImageFont.truetype(font_path, font_size, encoding="unic")

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Define button
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input()

def execute_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)

def get_wifi_info(interface='wlan0'):
    cmd = f"/usr/sbin/iwconfig {interface}"
    try:
        output = execute_command(cmd)
        essid = output.split('ESSID:"')[1].split('"')[0]
        freq = output.split('Frequency:')[1].split(' ')[0]
        quality = output.split('Link Quality=')[1].split(' ')[0]
        signal = output.split('Signal level=')[1].split(' ')[0]
        return essid, freq, quality, signal
    except Exception as e:
        print("Error getting wireless info:", e)
        return None, None, None, None

def signal_to_bars(signal):
    bars = ['\u2581', '\u2583', '\u2585', '\u2587']
    ranges = [
        (-100, -80), # 1 bar
        (-79, -67),  # 2 bars
        (-66, -56),  # 3 bars
        (-55, -30)   # 4 bars
    ]
    signal = int(signal) # cast to integer
    series = ""
    for i, (lower, upper) in enumerate(ranges):
        if signal >= lower:
            series += bars[i]
        else:
            break
    return series

def toggle_backlight():
    backlight.value = not backlight.value

while True:
    # Draw a black filled box to clear the image
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Get wireless interface stats 
    essid, freq, quality, signal = get_wifi_info()
    bars = signal_to_bars(signal)

    # Output wireless stats
    y = top
    draw.text((x, y), essid, font=font, fill="#711DB0")
    text_bbox = draw.textbbox((x, y), essid, font=font)
    text_height = text_bbox[3] - text_bbox[1]
    y += text_height + text_y_offset
    
    draw.text((x, y), "Freq: " + freq + " GHz", font=font, fill="#C21292")
    y += text_height + text_y_offset
   
    draw.text((x, y), "Quality: " + quality, font=font, fill="#EF4040")
    y += text_height + text_y_offset
   
    draw.text((x, y), "Signal: " + signal + " dBm", font=font, fill="#FFA732")
    y += text_height + text_y_offset + 5

    draw.text((x, y), "     " + bars, font=font, fill="#F3EDC8")

    # Display image
    disp.image(image, rotation)

    if not buttonA.value:
        toggle_backlight()

    time.sleep(.1)

