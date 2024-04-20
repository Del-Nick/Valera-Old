from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pytesseract import pytesseract
import cv2
import os
import numpy as np

pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'


path = 'Кабинеты/1 этаж.jpg'

arrow = Image.open('Кабинеты/Стрелка.png')

ar_width, ar_height = arrow.size

# new_array.show()
scale_factor = 0.2
arrow = arrow.resize((int(ar_width*scale_factor), int(ar_height*scale_factor)))




img = Image.open(path)

width, height = img.size
mg_rotate = img.rotate(-90)
mg_rotate = mg_rotate.crop((0, 0, width-1500, height))
draw = ImageDraw.Draw(img, mode='RGBA')
temp = 53.5*6
draw.rectangle((1843+temp, 1012, 1894+temp, 1091), fill="yellow")

label = '1-54'
font = ImageFont.truetype('Кабинеты/Montserrat-Bold.ttf', 36, encoding="unic")
line_height = sum(font.getmetrics())

fontimage = Image.new('L', (font.getsize(label)[0], line_height))
# И рисуем на ней белый текст
ImageDraw.Draw(fontimage).text((0, 0), label, fill=255, font=font)
fontimage = fontimage.rotate(90, resample=Image.BICUBIC, expand=True)
img.paste((0, 0, 0), box=(840+temp, 877), mask=fontimage)
arrow = arrow.rotate(-135)
img.paste(arrow, (900+temp, 750))

img.show()

# data = pytesseract.image_to_string(img)
# print(data)
# size = img.size
#
#
# new_image = img.crop((0, 0, width-1500, height))
# new_image.show()