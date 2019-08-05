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
print(additionalStr2)
folderPath += additionalStr1
Packages = []
try:
    os.remove("generated_script.py")
except:
    print("1")
    pass
"""
Создаем скрипт, который будет отвечать за работу бота.
В BotPackages находятся плагины для подключения к боту.
"""
newScript = open("generated_script.py","w+")
newScript.write("""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + """ + additionalStr2 + """)
massive = []
""");

for file in ([f for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f))]):
    newScript.write("import " + file[0:file.find(".")] + "\n")
    newScript.write("massive.append(" + file[0:file.find(".")] + ".Package)\n")
newScript.close()

import Core