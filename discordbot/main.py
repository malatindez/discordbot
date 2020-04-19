print(__name__)
#from BotPackages.music.picture import Picture
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