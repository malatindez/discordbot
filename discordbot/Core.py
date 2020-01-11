import sys
import os
import platform
import operator
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/DataBases/")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/localisation/")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\DataBases\\")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\localisation\\")
import discord
import asyncio
import generated_script
import DataBase
import operator
import sqlite3
core = None

def getCommand(command):
	command = command[1:]
	returnValue = ['',[]]
	for i in range(len(command)):
		if command[i] == " ":
			for j in range(i, len(command)):
				if command[j] != " ":
					returnValue[0] = command[:i].lower()
					command = command[j:]
					break;
			break;
		elif i == len(command)-1:
			returnValue[0] = command.lower()
			return returnValue
	buf = ""
	x = False
	for i in range(len(command)):
		if(command[i]==" "):
			x = True
		elif x and command[i] != " ":
			returnValue[1].append(buf)
			buf = command[i]
			x = False
		else:
			buf += command[i]
	if(len(buf)!=0):
		returnValue[1].append(buf)
	return returnValue

class Core:
    db = None
    client = discord.Client()
    plugins = []
    token = ""
    def addPlugin(self, plugin):
        # add plugin to plugins
        self.plugins.append(plugin)
        val = plugin.getUpdateFunctions()
        if val is not None:
            for function in val:
                self.client.loop.create_task(function(self))
        self.db.addGlobalUserValues(plugin.name, plugin.getAdditionalGlobalUserValues())
        self.db.addLocalUserValues(plugin.name, plugin.getAdditionalLocalUserValues())
        self.db.addGuildValues(plugin.name, plugin.getAdditionalGuildValues())
    
    def __init__(self):
        self.db = DataBase.DataBase()
        for plugin in generated_script.massive:
            self.addPlugin(plugin(self))
        for i in self.plugins:
            i.addDBRef(self.db);
        try:
            f = open('token'); self.token = f.readline().replace("\n", '').replace("\r", ''); f.close()
        except FileNotFoundError:
            print("Добавьте токен в папку со скриптом")
            exit()
        self.plugins.sort(key = operator.attrgetter('importance'))
    
    @client.event
    async def on_ready():
        print("Вошёл как " + core.client.user.name + ". Мой ID: " + str(core.client.user.id))
    def getEnabledPlugins(self, message):
        enabledPlugins = ["Service"]
        try: 
            enabledPlugins.extend(core.db.getEnabledPlugins(message.guild.id, 0))
        except:
            pass
        try:
            enabledPlugins.extend(core.db.getEnabledPlugins(message.guild.id, message.channel.id))
        except:
            pass
        return enabledPlugins

    @client.event
    async def on_message(message):
        # Пропуск сообщений, отправляемых ботом.
        if(message.author == core.client.user):
            return
        
        # Получаем данные в базе данных о гильдии, в которой было написано это сообщение.
        
        prefix = 0
        try:
            prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)
        except IndexError:
            for plugin in core.plugins:
                await plugin.on_guild_join(message.guild)
            prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)

        # Если первый символ сообщения не соответствует префиксу, установленному в этой гильдии - return
        for i in range(len(prefix)):
            if prefix[i] != message.content[i]:
                return

        enabledPlugins = core.getEnabledPlugins(message)
        print(core.plugins)
        # Превращаем сообщение " *prefix* name param1 param2 param3 ..." в список [name, [param1, param2, param3, ...]]
        command = getCommand(message.content)

        command[0] = command[0].lower()

        for plugin in core.plugins:
            if plugin.name in enabledPlugins:
                for PCommand in plugin.getCommands():
                    if PCommand[0] == command[0]:
                        if plugin.isAbleToUse(PCommand[1], message.author):
                            await PCommand[1](command[1], message, core)
                        return

    @client.event
    async def on_guild_join(guild):
        for plugin in core.plugins:
            await plugin.on_guild_join(guild)
core = Core()
core.client.run(core.token)