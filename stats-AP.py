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
text_y_offset = 3
x = 0

# Load FiraCode TTF Font
font_path = '/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf'
font_size = 22
font = ImageFont.truetype(font_path, font_size, encoding="unic")

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Define button
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input()

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)

def toggle_backlight():
    backlight.value = not backlight.value

while True:
    # Draw a black filled box to clear the image
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Collect basic system stats
    cmd = "/usr/bin/hostname -I | cut -d\' \' -f1"
    output = execute_command(cmd)
    IP = "IP: " + output

    cmd = "/usr/bin/pidof hostapd | wc -l | awk '{printf \"Hotspot: %s\", $1 == 1 ? \"Active\" : \"Down\"}'"
    Hostapd = execute_command(cmd)

    cmd = "/usr/bin/vnstat -i wlan0 | grep tx: | awk '{printf \"Data Tx: %d %s\", $5,$6}'"
    DataTx = execute_command(cmd) 

    cmd = "/usr/bin/free -m | awk 'NR==2{printf \"Mem: %sMB %.2f%%\", $3,$3*100/$2 }'"
    MemUsage = execute_command(cmd) 

    cmd = "/usr/bin/top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = execute_command(cmd) 

    cmd = "/usr/bin/cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long
    Temp = execute_command(cmd) 

    # Write five lines of stats
    y = top
    draw.text((x, y), IP, font=font, fill="#59D5E0")
    text_bbox = draw.textbbox((x, y), IP, font=font)
    text_height = text_bbox[3] - text_bbox[1]
    y += text_height + text_y_offset

    draw.text((x, y), Hostapd, font=font, fill="#F5DD61")
    y += text_height + text_y_offset
    
    draw.text((x, y), DataTx, font=font, fill="#FAA300")
    y += text_height + text_y_offset

    draw.text((x, y), MemUsage, font=font, fill="#F4538A")
    y += text_height + text_y_offset

    draw.text((x, y), Temp, font=font, fill="#6420AA")
    y += text_height + text_y_offset

    draw.text((x, y), CPU, font=font, fill="#7F27FF")
   
    # Display image
    disp.image(image, rotation)

    if not buttonA.value:
        toggle_backlight()

    time.sleep(.1)

