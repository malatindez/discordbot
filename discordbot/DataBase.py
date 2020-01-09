import sqlite3
import json
class DataBase():
    def __init__(self):
        self.db = sqlite3.connect("DataBase.sql")
        self.cursor = self.db.cursor()
        try:
            self.cursor.execute("CREATE TABLE Guilds('id' int64, 'channelLanguages' str, 'enabledPlugins' str)")
            self.cursor.execute("CREATE TABLE Users('id' int64)")
        except sqlite3.OperationalError: pass;

    def __del__(self):
        self.commit()
        self.db.close()
 
    def commit(self):
        self.db.commit()
    def addGlobalUserValues(self, name, valuesList):
        if valuesList is None: 
            return
        for i in range(len(valuesList)):
            try:
                self.cursor.execute("ALTER TABLE Users ADD COLUMN '" + name +
                                   valuesList[i][0] + "' " + valuesList[i][1])
            except sqlite3.OperationalError: pass;

    def addLocalUserValues(self, name, valuesList):
        if valuesList is None: 
            return
        for i in range(len(valuesList)):
            try:
                self.cursor.execute("ALTER TABLE Guilds ADD COLUMN '" + name +
                                   valuesList[i][0] + "' " + valuesList[i][1])
            except sqlite3.OperationalError: pass;

    def addGuildValues(self, name, valuesList):
        if valuesList is None: 
            return
        for i in range(len(valuesList)):
            try:
                self.cursor.execute("ALTER TABLE Guilds ADD COLUMN '" + name +
                                   valuesList[i][0] + "' " + valuesList[i][1])
            except sqlite3.OperationalError: pass;

    def addGuild(self, id):
        a = len(self.cursor.execute("PRAGMA table_info('Guilds')").fetchall())
        s = "INSERT INTO Guilds VALUES(" + str(id) + ", '{}', '{}' "
        for i in range(a - 3): s += ", 0"
        self.cursor.execute(s + ")")

    def addChannelLanguage(self, guildID, channelID, language):
        self.cursor.execute("SELECT channelLanguages FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x) 
        v[str(channelID)] = language
        self.cursor.execute("UPDATE Guilds SET channelLanguages = '" + json.dumps(v) +
                           "' WHERE id = " + str(guildID))
    
    def getChannelLanguage(self, guildID, channelID):
        self.cursor.execute("SELECT channelLanguages FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        return v[str(channelID)]



    def addEnabledPlugin(self, guildID, channelID, plugin):
        self.cursor.execute("SELECT enabledPlugins FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        if channelID not in v:
            v[channelID] = []
        if plugin not in v[channelID]:
            v[channelID].append(plugin)
        self.cursor.execute("UPDATE Guilds SET enabledPlugins = '" + json.dumps(v) +
                           "' WHERE id = " + str(guildID))
    
    def remEnabledPlugin(self, guildID, channelID, plugin):
        self.cursor.execute("SELECT enabledPlugins FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        v[str(channelID)].remove(plugin)
        self.cursor.execute("UPDATE Guilds SET enabledPlugins = '" + json.dumps(v) +
                           "' WHERE id = " + str(guildID))

    def getEnabledPlugins(self, guildID, channelID):
        self.cursor.execute("SELECT enabledPlugins FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        return v[str(channelID)]



    def getGlobalUserData(self, name, dataName, userID):
        self.cursor.execute("SELECT " + name + dataName + " FROM Users WHERE id = " + str(userID))
        return self.cursor.fetchall()[0][0]

    def writeGlobalUserData(self, name, dataName, userID, newValue):
        self.cursor.execute("SELECT " + name + dataName + " FROM Users WHERE id = " + str(userID))
        s = "INSERT INTO Users Values(" + str(userID) 
        a = len(self.cursor.execute("PRAGMA table_info('Users')").fetchall())
        for i in range(a - 1): s += ", 0"
        s += ")"
        self.cursor.execute(s)
        self.cursor.execute("UPDATE Users SET " + name + dataName + " = \"" +
                           str(newValue) + "\" WHERE id = " + str(userID))

    def getLocalUserData(self, name, dataName, guildID, userID):
        self.cursor.execute("SELECT " + name + dataName + " FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        return v[str(userID)]

    def writeLocalUserData(self, name, dataName, guildID, userID, newValue):
        self.cursor.execute("SELECT " + name + dataName + " FROM Guilds WHERE id = " + str(guildID))
        x = self.cursor.fetchall()[0][0]
        v = json.loads(x)
        v[userID] = newValue
        self.cursor.execute("UPDATE Guilds SET" + name + dataName + " = \"" + 
                            str(json.dumps(v)) + "\" WHERE id = " + str(guildID))

    def getGuildData(self, name, dataName, guildID):
        self.cursor.execute("SELECT " + name + dataName + " FROM Guilds WHERE id = " + str(guildID))
        x =  self.cursor.fetchall()
        return x[0][0]

    def writeGuildData(self, name, dataName, guildID, value):
        self.cursor.execute("UPDATE Guilds SET " + name + dataName + " = '" + str(value) + "' WHERE id = " + str(guildID))