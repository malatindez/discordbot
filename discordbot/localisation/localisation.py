import os
import json
class Localisation:
    data = []
    """
    [
        [
            "name", 
            [
                [
                    "en-EN",
                    json
                ],
                [
                    "ru-RU",
                    json
                ]
            ]
        ], ...
    ]
    """
    def __init__(self):
        FOLDER_PATH = os.path.dirname(os.path.realpath(__file__)) 
        for folder in ([f for f in os.listdir(FOLDER_PATH) if os.path.isdir(os.path.join(FOLDER_PATH, f))]):
            if folder == "__pycache__":
                continue
            for file in ([f for f in os.listdir(FOLDER_PATH + "/" + folder) if os.path.isfile(os.path.join(FOLDER_PATH + "/" + folder, f))]):
                f = open(FOLDER_PATH + "/" + folder + "/" + file, "r")
                x = False
                for element in self.data:
                    if element[0] == file[:file.find(".")]:
                        try:
                            element[1].append([folder, json.loads(f.read())])
                        except:
                            pass
                        x = True
                        break;
                if not x:
                    var = [file[:file.find(".")], []]
                    try:
                        var[1].append([folder, json.loads(f.read())])
                    except:
                        pass
                    self.data.append(var)
                f.close()
    def getText(self, packageName, value, language):
        for element in self.data:
            if element[0] == packageName:
                for lang in element[1]:
                    if(lang[0] == language):
                        try:
                            return lang[1][value]
                        except:
                            return "none"
                for lang in element[1]:
                    if(lang[0] == "en-EN"):
                        try:
                            return lang[1][value]
                        except:
                            return "none"
        return "none"
    def getAvailableLanguages(self):
        listOfLanguages = []
        for element in self.data:
            for lang in element[1]:
                x = True
                for elm in listOfLanguages:
                    if elm == lang[0]:
                        x = False
                        break;
                if x:
                    listOfLanguages.append(lang[0])
        return listOfLanguages