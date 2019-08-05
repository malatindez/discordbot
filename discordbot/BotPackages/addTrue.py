import sys
import time
import asyncio
import os
import discord
import platform
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
import Utils
import Package as pckg

class Package(pckg.Package):
    name = "addTrue"

    def __init__(self, LocalisationReference):
        self.LocalisationReference = LocalisationReference
    def getCommands(self):
        return [
            ["help", self.help],
            ["settrue", self.setTrue],
            ["settrueu", self.setTrueU]
        ]

    async def on_member_update(self, before, after):
        if after.activity is None:
            return
        if after.activity.application_id == 568473437484482561:
            role = after.guild.get_role(int(self.db.SELECT("addTrueTrueRole", ["*"], "")[0][0]))
            nickname = after.activity.details[5:] + "✔"
            if after.nick != nickname or not (role in after.roles):
                roles = after.roles
                if not (role in after.roles):
                    roles.append(role)
                await after.edit(nick = nickname, roles = roles)


    async def help(self, params, message, client):
        await message.delete(delay = 5);
        def lGetText(value):
            return self.getText(message.channel.id, value)
        embed = discord.Embed(
            title = lGetText("helpTitle"),
            color = 0xff84ff)
        embed.add_field(name="help", value= lGetText("help"), inline=False)
        embed.add_field(name="setTrue", value= lGetText("setTrue"), inline=False)
        embed.add_field(name="setTrueU", value= lGetText("setTrueU"), inline=False)
        await message.channel.send(embed=embed, delete_after = 30)
        
    async def setTrue(self, params, message, client):
        await message.delete(delay = 5);
        role = message.guild.get_role(int(params[0].replace("<@&", "").replace(">","")))
        if role is None:
            await message.channel.send(self.getText(message.channel.id, "setTrueError"), delete_after = 30)
            return
        self.db.DROP_TABLE("addTrueTrueRole")
        self.db.CREATE_TABLE("addTrueTrueRole", [["trueRole", "str"]])
        self.db.INSERT("addTrueTrueRole", [["trueRole", str(params[0].replace("<@&", "").replace(">",""))]])
        await message.channel.send(self.getText(message.channel.id, "setTrueSuccess"), delete_after = 30)
    async def setTrueU(self, params, message, client):
        await message.delete(delay = 5);

    def GiveDataBaseReference(self, db):
        self.db = db
        try:
            db.CREATE_TABLE("addTrueTrueRole", [["trueRole", "str"]])
        except:
            pass
