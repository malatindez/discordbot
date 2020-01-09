import json
class Localisation:
    def __init__(self, path):
        self.data = json.loads(open(path, 'r').read())
    def getText(self, value, language):
        return self.data[language][value]
