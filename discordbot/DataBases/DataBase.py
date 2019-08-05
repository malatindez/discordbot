import sqlite3
import platform
import os
class DataBase:
    DaBe = 0
    cursor = 0 
    def __init__(self, dbname):
        self.DaBe = sqlite3.connect(dbname)
        self.cursor = self.DaBe.cursor()
    def __del__(self):
        self.DaBe.commit()
        self.DaBe.close()
    def CREATE_TABLE(self, TableName, data):
        string = "CREATE TABLE " + TableName + "("
        for i in range(len(data)):
            string+= "'" + data[i][0] +  "' " + data[i][1]
            if len(data)-1 == i:
                string += ")"
            else:
                string += ", "
        self.cursor.execute(string)
        self.DaBe.commit()
    def DROP_TABLE(self, TableName):
        self.cursor.execute("DROP TABLE " + TableName)
    def TRUNCATE_TABLE(self,TableName):
        self.cursor.execute("TRUNCATE " + TableName)
    def ALTER_TABLE_ADD(self, TableName, name, type):
        self.cursor.execute("ALTER TABLE " + TableName + " ADD " + name + " " + type)
    def ALTER_TABLE_MODIFY(self, TableName, name, newType):
        self.cursor.execute("ALTER TABLE " + TableName + " MODIFY " +  name + " " + newType)
    def INSERT(self, TableName, data):
        string = "INSERT INTO " + TableName + "("
        for i in range(len(data)):
            string += "'" + data[i][0] + "'"
            if(i!=len(data)-1):
                string+=', '
        string += ") VALUES("
        for i in range(len(data)):
            string += "'" + data[i][1]+ "'"
            if(i!=len(data)-1):
                string+=', '
        string+=")"
        self.cursor.execute(string)
        self.DaBe.commit()
    def UPDATE(self, TableName, set, whereStatement):
        string =  "UPDATE " + TableName + " SET "
        for i in range(len(set)):
            string += set[i][0] + " = '" + set[i][1] + "'"
            if i != len(set)-1:
                string+=", "
        string += " WHERE " + whereStatement
        self.cursor.execute(string)
        self.DaBe.commit()
    def DELETE(self, TableName, whereStatement):
        string = "DELETE FROM " + TableName + " WHERE " + whereStatement
        self.cursor.execute(string)
    def SELECT(self, TableName, columns, whereStatement):
        string = "SELECT "
        for i in range(len(columns)):
            string += columns[i]
            if i != len(columns)-1:
                string += ","
        string += " FROM " + TableName
        if(whereStatement != ""):
            string += " WHERE " + whereStatement
        self.cursor.execute(string)
        return self.cursor.fetchall()

class DB(DataBase):
    def __init__(self, plugins):
        if platform.system() == "Linux":
            super(DB,self).__init__("DataBases/DataBase.db")
        elif platform.system() == "Windows":
            super(DB, self).__init__(os.path.dirname(os.path.realpath(__file__)) + "\\DataBase.db")
        create_table_value1 = [["id", "int"]]
        create_table_value2 = [["id", "int"], ["prefix","string"], ["plugin_channels", "string"]]
        for plugin in plugins:
            x1 = plugin.getAdditionalUserValues()
            x2 = plugin.getAdditionalGuildValues()
            plugin.GiveDataBaseReference(self)
            if x1 is not None:
                create_table_value1 += x1
            if x2 is not None:
                create_table_value2 += x2
        try:
            self.CREATE_TABLE("Users", create_table_value1)
            self.CREATE_TABLE("Guilds", create_table_value2)
            self.CREATE_TABLE("ChannelsAndLanguages", [["channelID", "string"], ["language", "string"]])
        except:
            pass
    def AddUser(self, id):
        self.INSERT("Users", ["id", str(id)])
    def EditUser(self, id, editValues):
        self.UPDATE("Users", editValues, "id = " + str(id))
    def GetUserData(self, id):
        return self.SELECT("Users", ["*"], "id = " + str(id))
    def AddGuild(self, id, prefix, plugin_channels):
        self.INSERT("Guilds", [["id", str(id)], ["prefix", str(prefix)], ["plugin_channels", str(plugin_channels)]])

    def EditGuild(self, id, prefix, plugin_channels):
        self.UPDATE("Guilds", [["prefix", str(prefix)], ["plugin_channels", plugin_channels]], "id = " + str(id))

    def GetGuildData(self, id):
        return self.SELECT("Guilds", ["*"], "id = " + str(id))
    def GetPrefix(self, id):
        pref = self.SELECT("Guilds", ["prefix"], "id = " + str(id))
        return pref[0]
    def GetEnabledPlugins(self, id):
        ep = self.SELECT("Guilds", ["plugin_channels"], "id = " + str(id))
        return ep[0]
    
    def RemoveGuild(self, id):
        self.DELETE("Guilds", "id = " + str(id))