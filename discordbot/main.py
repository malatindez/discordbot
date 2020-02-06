print(__name__)

if __name__ == "__main__":
    import sys
    import os
    import importlib.util
    import platform



    folderPath = os.path.dirname(os.path.realpath(__file__))
    additionalStr1 = ""; additionalStr2 = ""

    if platform.system() == "Linux":
        additionalStr1 = "/BotPackages/";   additionalStr2 = "\"/BotPackages/\""
    elif platform.system() == "Windows":
        additionalStr1 = "\\BotPackages\\"; additionalStr2 = "\"\\\\BotPackages\\\\\""
    folderPath += additionalStr1
    Packages = []
    try:
        os.remove("generated_script.py")
    except FileNotFoundError:
        pass
    """
    Создаем скрипт, который будет отвечать за работу бота.
    В BotPackages находятся плагины, которые будут использоваться ботом.
    """
    newScript = open("generated_script.py","w+")
    newScript.write("""
import sys
import os
massive = []
""");

    for folder in ([f for f in os.listdir(folderPath) if os.path.isdir(os.path.join(folderPath, f))]):
        if folder == "__pycache__":
            continue
        if platform.system() == "Linux":
            newScript.write("sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + " + additionalStr2 + " + \"/" + folder +"/\")\n")
        elif platform.system() == "Windows":
            newScript.write("sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + " + additionalStr2 + " + \"\\\\" + folder +"\\\\\")\n")
        newScript.write("import " + folder + "\n")
        newScript.write("massive.append(" + folder + ".Package)\n")
    newScript.close()
    import Core
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
thumbnail = 'https://i.ytimg.com/vi/PDeTO26fRVQ/maxresdefault.jpg'
title = 'blackbear - idfc (Lyrics)'
channel = 'Aurora Vibes'
duration = 190
font = ImageFont.truetype("arial.ttf", 12)
if '-' in title:
    channel = ""
    while True:
        if title[0] == '-':
            title = title[2:]
            break
        channel += title[0]
        title = title[1:]
def bettertime(duration):
    x = [int(duration / 60), duration % 60]
    for i in range(2):
        if x[i] >= 10:
            x[i] = str(x[i])
        else:
            x[i] = "0" + str(x[i])
    return x
durationtxt = '{x[0]}:{x[1]}' + '/{x[0]}:{x[1]}'.format(x=bettertime(duration))
im = Image.open("template.png")

img = Image.open(BytesIO(requests.get(thumbnail).content))
print(img.size)

img.thumbnail((484, 484), Image.ANTIALIAS)
im.paste(img, (82,107))
images = []

for i in range(duration):
    im2 = im.copy()
    draw = ImageDraw.Draw(im2)
    x, y = 615 + int(i*531/duration), 386
    draw.line((615, 386, x,y), fill = (234,39,39), width=3)
    draw.ellipse([(x-5,y+5),(x-5,y+5)],fill=(234,39,39))
    draw.text((610, 430), (durationtxt).format(x=bettertime(i)), font=font)
    images.append(im2)
images[0].save('lol.gif', save_all=True, append_images=images[1:], optimize=True, duration=1000, loop=0)
"""
