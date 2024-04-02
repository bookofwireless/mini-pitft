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
# Move left to right keeping track of the current x position
x = 0

# Load DejaVu TTF Font
# Install with: sudo apt-get install ttf-dejavu
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_size = 24
font = ImageFont.truetype(font_path, font_size, encoding="unic")

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)

cmd = "nmcli device wifi"

while True:
    # Draw a black filled box to clear the image
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    output = execute_command(cmd)

    wifi_info = []
    lines = output.strip().split('\n')
    headers = lines[0].split()
    data = lines[1].split()

    indices = [headers.index(header) for header in ['SSID', 'CHAN', 'SIGNAL', 'SECURITY' ]]
    for line in lines[1:]:
        parsed_line = line.split()
        data = [parsed_line[i] for i in indices]
        wifi_info.append(data)

    SSID, CHAN, SIGNAL, SECURITY = wifi_info[0]

    # Output wifi statistics
    y = top
    draw.text((x, y), SSID, font=font, fill="#FFFFFF")
    text_bbox = draw.textbbox((x, y), SSID, font=font)
    text_height = text_bbox[3] - text_bbox[1]
    y += text_height + text_y_offset
    
    draw.text((x, y), "Channel: " + CHAN, font=font, fill="#FFFF00")
    y += text_height + text_y_offset
   
    draw.text((x, y), "Signal: " + SIGNAL, font=font, fill="#00FF00")
    y += text_height + text_y_offset + 10
    
    #draw.text((x, y), "Rate: " + RATE , font=font, fill="#0000FF")
    #y += text_height + text_y_offset
    
    draw.text((x, y), "Bars: " + SECURITY, font=font, fill="#FF00FF")

    # Display image
    disp.image(image, rotation)
    time.sleep(.1)

