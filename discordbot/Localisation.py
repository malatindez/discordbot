import json
class Localisation:
    def __init__(self, path):
        self.data = json.loads(open(path, 'r',encoding='utf-8').read())
    def getText(self, value, language):
        return self.data[language][value]
