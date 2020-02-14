
import sys
import os
import platform
import asyncio
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
import Localisation
class Package:
    name = ""
    importance = 0
    def __init__(self, core):
        self.core = core
        if platform.system() == "Linux":
            self.localisation = Localisation.Localisation(os.path.dirname(os.path.realpath(__file__)) + "/" + self.name  + "/" + self.name + ".json")
        elif platform.system() == "Windows":
            self.localisation = Localisation.Localisation(os.path.dirname(os.path.realpath(__file__)) + "\\" + self.name + "\\" + self.name + ".json")
    def getChannelLanguage(self, guildID, channelID):
        try:
            return self.db.getChannelLanguage(guildID, channelID)
        except KeyError: return "English"

    def getText(self, guildID, channelID, value):
        return self.localisation.getText(value, self.getChannelLanguage(guildID, channelID))

    def getDescription(self,guildID, channelID):
        return self.getText(guildID, channelID, "description")
    def addDBRef(self, db):
        self.db = db
    # u can overwrite the next functions 
    
    #return True if user can use this command
    #return False if not
    def isAbleToUse(self, commandName, member):
        return True

    # that function called before calling a command from package
    # params:
    # message - discord.Message()
    # command - [name, [param1, param2, param3, ...]]
    async def firstCall(self, message, command):
        pass

    # add data to db for your plugin
    # that's global data which doesn't depends on the guild id
    # return [["dataName", "type"], ["dataName", "type"]]
    # type - SQL type

    # to get access to that data you can call:
    # db.getGlobalUserData(self.name, dataName,userID)
    # db.writeGlobalUserData(self.name, dataName, userID, newValue)
    def getAdditionalGlobalUserValues(self):
        return None    
    
    # add data to db for your plugin
    # that's local data which depends on the guild id
    # return [["dataName", "type"], ["dataName", "type"]]
    # type - SQL type

    # to get access to that data you can call:
    # db.getGlobalUserData(self.name, dataName, guildID, userID)
    # db.writeGlobalUserData(self.name, dataName, guildID, userID, newValue)
    def getAdditionalLocalUserValues(self):
        return None

    # add data to db for your plugin
    # return [["dataName", "type"], ["dataName", "type"]]
    # type - SQL type

    # to get access to that data you can call
    # db.getGuildData(self.name, dataName, guildID)
    # db.writeGuildData(self.name, dataName, guildID, newValue)
    def getAdditionalGuildValues(self):
        return None

    # returns functions which will be added in client.loop
    # async def a(self, core):
    #   pass
    # async def b(self, core):
    #   pass
    # return [a(),b()]
    def getUpdateFunctions(self):
        return None
    
    # returns list of commands and reference to functions of them
    # return [
    #            [name(string), importance(int), func()], 
    #            [name(string), importance(int), func()]
    #        ]
    def getCommands(self):
        return None
    def post__init__(self):
        pass
    async def on_message(self, message):
        pass
    async def on_raw_message_delete(self, payload):
        pass
    async def on_message_edit(self, before, after):
        pass
    async def on_reaction_add(self, reaction, user):
        pass
    async def on_raw_reaction_add(self, payload):
        pass
    async def on_reaction_remove(self, reaction, user):
        pass
    async def on_raw_reaction_remove(self, payload):
        pass
    async def on_reaction_clear(self, message, reactions):
        pass
    async def on_raw_reaction_clear(self, payload):
        pass
    async def on_private_channel_delete(self, channel):
        pass
    async def on_private_channel_create(self, channel):
        pass
    async def on_private_channels_update(self, before, after):
        pass
    async def on_private_channel_pins_update(self, channel, last_pin):
        pass
    async def on_guild_channel_delete(self, channel):
        pass
    async def on_guild_channel_create(self, channel):
        pass
    async def on_guild_channel_update(self, before, after):
        pass
    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass
    async def on_guild_integrations_update(self, guild):
        pass
    async def on_webhooks_update(self, channel):
        pass
    async def on_member_join(self, member):
        pass
    async def on_member_remove(self, member):
        pass
    async def on_member_update(self, before, after):
        pass
    async def on_guild_join(self, guild):
        pass
    async def on_guild_remove(self, guild):
        pass
    async def on_guild_update(self, guild):
        pass
    async def on_guild_role_create(self, role):
        pass
    async def on_guild_role_delete(self, role):
        pass
    async def on_guild_role_update(self, before, after):
        pass
    async def on_guild_emojis_update(self, guild, before, after):
        pass
    async def on_voice_state_update(self, member, before, after):
        pass
    async def on_member_ban(self, guild, user):
        pass
    async def on_member_unban(self, guild, user):
        pass