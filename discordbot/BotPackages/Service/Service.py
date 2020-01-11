import platform
import sys
import os
import discord
import json
import asyncio

if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
import package

class Package(package.Package):

    def __init__(self, core):
        self.name = "Service"
        super(Package, self).__init__(core)
        self.importance = 255

    def getAdditionalGuildValues(self):
        return [["Prefix", "str"]]

    def getCommands(self):
        return [["help", self.help], 
                ["glang", self.getLanguage], ["glanguage", self.getLanguage], ["getlang", self.getLanguage], ["getlanguage", self.getLanguage], ["gl", self.getLanguage],
               ["clang", self.changeLanguage], ["clanguage", self.changeLanguage], ["changelang", self.changeLanguage], ["changelanguage", self.changeLanguage], ["cl", self.changeLanguage],
              ["plist", self.pluginList], ["pluginlist", self.pluginList], ["pl", self.pluginList],
              ["eplist", self.enabledPluginList], ["enabledplist", self.enabledPluginList], ["epluginlist", self.enabledPluginList], ["epl", self.enabledPluginList], ["enabledpluginlist", self.enabledPluginList],
              ["cplugin", self.connectPlugin], ["connectplugin", self.connectPlugin], ["connectp", self.connectPlugin], ["cp", self.connectPlugin],
              ["disconnectplugin", self.disconnectPlugin], ["dplugin", self.disconnectPlugin], ["dcplugin", self.disconnectPlugin], ["dcp", self.disconnectPlugin], ["dp", self.disconnectPlugin],
             ["sdb", self.saveDB ],
             ["cprefix", self.changePrefix], ["changeprefix", self.changePrefix]]
    
    def isAbleToUse(self, commandName, user):
        return user.guild_permissions.administrator or user.id == 595328091962867717
    
    def getUpdateFunctions(self):
        return [self.saveDBUpdate]


    async def saveDBUpdate(self, core):
        while True:
            try:
                print("Database was successfully saved!")
                self.db.commit()
            except:
                print("error during saving database")
            await asyncio.sleep(60)

    async def saveDB(self, params, message, core):
        self.db.commit();
        await message.channel.send("success");

    async def help(self, params, message, core):
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "help"),
                             description = self.getText(message.guild.id, message.channel.id, "helpDescription"))
        embed.add_field(name = "gLang",
                        value = self.getText(message.guild.id, message.channel.id, "helpGetLanguage"),
                        inline = False)
        embed.add_field(name = "cLang",
                        value = self.getText(message.guild.id, message.channel.id, "helpChangeLanguage"),
                        inline = False)
        embed.add_field(name = "pList",
                        value = self.getText(message.guild.id, message.channel.id, "helpPluginList"),
                        inline = False)
        embed.add_field(name = "epList",
                        value = self.getText(message.guild.id, message.channel.id, "helpEnabledPluginList"),
                        inline = False)
        embed.add_field(name = "cPlugin",
                        value = self.getText(message.guild.id, message.channel.id, "helpConnectPlugin"),
                        inline = False)
        embed.add_field(name = "discPlugin",
                        value = self.getText(message.guild.id, message.channel.id, "helpDisconnectPlugin"),
                        inline = False)
        await message.channel.send(embed = embed)

    async def getLanguage(self, params, message, core):
        rmessage = ""
        try:
            rmessage = self.getText(message.guild.id, message.channel.id, "language")
        except KeyError:
            self.db.addChannelLanguage(message.guild.id, message.channel.id, "English")
            rmessage = "English"
        await message.channel.send(rmessage)

    async def changeLanguage(self, params, message, core):
        prevLanguage = "English"
        try:
            prevLanguage = self.db.getChannelLanguage(self.guild.id, message.channel.id)
        except:
            pass
        self.db.addChannelLanguage(message.guild.id, message.channel.id, params[0])
        rmessage = ""
        try:
            rmessage= self.getText(message.guild.id, message.channel.id, "changeLanguageSuccess")
        except:
            self.db.addChannelLanguage(message.guild.id, message.channel.id, prevLanguage)
            rmessage = self.getText(message.guild.id, message.channel.id, "changeLanguageError")
        await message.channel.send(rmessage)

    async def pluginList(self, params, message, core):
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "pluginList"))
        for plugin in core.plugins:
            embed.add_field(name = plugin.getText(message.guild.id, message.channel.id, "name") + " (" + plugin.name + ")",
                            value = plugin.getText(message.guild.id, message.channel.id, "description"), 
                            inline = False)
        await message.channel.send(embed=embed)

    async def enabledPluginList(self, params, message, core):
        enabledPlugins = core.getEnabledPlugins(message)
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "enabledPluginList"))
        for plugin in core.plugins:
            if plugin.name in enabledPlugins:
                embed.add_field(name = plugin.getText(message.guild.id, message.channel.id, "name") + " (" + plugin.name + ")",
                            value = plugin.getText(message.guild.id, message.channel.id, "description"), 
                            inline = False)
        await message.channel.send(embed=embed)

    async def connectPlugin(self, params, message, core):
        x = core.plugins
        f = False
        for i in x:
            if i.name == params[0]:
                f = True
                break
        if not f:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectPluginErrorNotFound"))
            return
        enabledPlugins = core.getEnabledPlugins(message)

        if params[0] in enabledPlugins:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectPluginErrorAlreadyExists"))
            return
        self.db.addEnabledPlugin(message.guild.id, message.channel.id, params[0])
        
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectPluginSuccess"))
    
    async def disconnectPlugin(self, params, message, core):
        enabledPlugins = core.getEnabledPlugins(message)
        if params[0] not in enabledPlugins:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "disconnectPluginErrorNotFound"))
            return
        self.db.remEnabledPlugin(message.guild.id, message.channel.id, params[0])
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "disconnectPluginSuccess"))

    async def changePrefix(self, params, message, core):
        if(len(params) == 0):
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "wrongPrefix"))
            return

        if len(params[0]) > 4:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "tooBigPrefix"))
            return

        self.db.writeGuildData("Service", "Prefix", str(message.guild.id), params[0])
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "prefixSuccessfullyChanged").format(params[0]))

    async def on_guild_join(self, guild):
        self.db.addGuild(guild.id)
        self.db.writeGuildData(self.name, "prefix", guild.id, "!")
        #self.db.addEnabledPlugins(guild.id, 0, "Service")
