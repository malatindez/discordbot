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

def getCommand(command, prefixLen):
	command = command[prefixLen:]
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
        plugin.post__init__() # calling a postinit phase
    
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
        # Пропуск картинок и однобуквенных сообщений
        if len(message.content) <= 1:
            return
        # Получаем данные в базе данных о гильдии, в которой было написано это сообщение.
        
        prefix = 0
        try:
            prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)
        except IndexError:
            for plugin in reversed(core.plugins):
                await plugin.on_guild_join(message.guild)
            prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)
        prefix = str(prefix)
        # Если первый символ сообщения не соответствует префиксу, установленному в этой гильдии - return
        for i in range(len(prefix)):
            if prefix[i] != message.content[i]:
                for plugin in core.plugins:
                    await plugin.on_message(message)
                return

        enabledPlugins = core.getEnabledPlugins(message)
        # Превращаем сообщение " *prefix* name param1 param2 param3 ..." в список [name, [param1, param2, param3, ...]]
        command = getCommand(message.content, len(prefix))

        command[0] = command[0].lower()

        for plugin in core.plugins:
            if plugin.name in enabledPlugins:
                for PCommand in plugin.getCommands():
                    if PCommand[0] == command[0]:
                        if plugin.isAbleToUse(PCommand[1], message.author):
                            await plugin.firstCall(message, command)
                            await PCommand[1](command[1], message, core)
                        return
        for plugin in core.plugins:
            await plugin.on_message(message)
    @client.event
    async def on_raw_message_delete(payload):
        for plugin in core.plugins:
            await plugin.on_raw_message_delete(payload)

    @client.event
    async def on_message_edit(before, after):
        for plugin in core.plugins:
            await plugin.on_message_edit(before, after)

    @client.event
    async def on_reaction_add(reaction, user):
        for plugin in core.plugins:
            await plugin.on_reaction_add(reaction, user)

    @client.event
    async def on_raw_reaction_add(payload):
        for plugin in core.plugins:
            await plugin.on_raw_reaction_add(payload)

    @client.event
    async def on_reaction_remove(reaction, user):
        for plugin in core.plugins:
            await plugin.on_reaction_remove(reaction, user)

    @client.event
    async def on_raw_reaction_remove(payload):
        for plugin in core.plugins:
            await plugin.on_raw_reaction_remove(payload)

    @client.event
    async def on_reaction_clear(message, reactions):
        for plugin in core.plugins:
            await plugin.on_raw_reaction_remove(message, reactions)

    @client.event
    async def on_raw_reaction_clear(payload):
        for plugin in core.plugins:
            await plugin.on_raw_reaction_clear(payload)

    @client.event
    async def on_private_channel_delete(channel):
        for plugin in core.plugins:
            await plugin.on_private_channel_delete(channel)

    @client.event
    async def on_private_channel_create(channel):
        for plugin in core.plugins:
            await plugin.on_private_channel_create(channel)

    @client.event
    async def on_private_channels_update(before, after):
        for plugin in core.plugins:
            await plugin.on_private_channels_update(before, after)

    @client.event
    async def on_private_channel_pins_update(channel, last_pin):
        for plugin in core.plugins:
            await plugin.on_private_channel_pins_update(channel, last_pin)

    @client.event
    async def on_guild_channel_delete(channel):
        for plugin in core.plugins:
            await plugin.on_guild_channel_delete(channel)

    @client.event
    async def on_guild_channel_create(channel):
        for plugin in core.plugins:
            await plugin.on_guild_channel_create(channel)

    @client.event
    async def on_guild_channel_update(before, after):
        for plugin in core.plugins:
            await plugin.on_guild_channel_update(before, after)

    @client.event
    async def on_guild_channel_pins_update(channel, last_pin):
        for plugin in core.plugins:
            await plugin.on_guild_channel_pins_update(channel, last_pin)
        
    @client.event
    async def on_guild_integrations_update(guild):
        for plugin in core.plugins:
            await plugin.on_guild_integrations_update(guild)

    @client.event
    async def on_webhooks_update(channel):
        for plugin in core.plugins:
            await plugin.on_webhooks_update(channel)

    @client.event
    async def on_member_join(member):
        for plugin in core.plugins:
            await plugin.on_member_join(member)

    @client.event
    async def on_member_remove(member):
        for plugin in core.plugins:
            await plugin.on_member_remove(member)

    @client.event
    async def on_member_update(before, after):
        for plugin in core.plugins:
            await plugin.on_member_update(before, after)

    @client.event
    async def on_guild_join(guild):
        for plugin in core.plugins:
            await plugin.on_guild_join(guild)

    @client.event
    async def on_guild_remove(guild):
        for plugin in core.plugins:
            await plugin.on_guild_remove(guild)

    @client.event
    async def on_guild_update(guild):
        for plugin in core.plugins:
            await plugin.on_guild_update(guild)

    @client.event
    async def on_guild_role_create(role):
        for plugin in core.plugins:
            await plugin.on_guild_role_create(role)

    @client.event
    async def on_guild_role_delete(role):
        for plugin in core.plugins:
            await plugin.on_guild_role_delete(role)

    @client.event
    async def on_guild_role_update(before, after):
        for plugin in core.plugins:
            await plugin.on_guild_role_update(before, after)

    @client.event
    async def on_guild_emojis_update(guild, before, after):
        for plugin in core.plugins:
            await plugin.on_guild_emojis_update(guild, before, after)

    @client.event
    async def on_voice_state_update(member, before, after):
        for plugin in core.plugins:
            await plugin.on_voice_state_update(member, before, after)

    @client.event
    async def on_member_ban(guild, user):
        for plugin in core.plugins:
            await plugin.on_member_ban(guild, after)

    @client.event
    async def on_member_unban(guild, user):
        for plugin in core.plugins:
            await plugin.on_member_unban(guild, user)
core = Core()
core.client.run(core.token)