import sys
import os
import asyncio
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
import Utils
class Package:
    name = ""
    db = None
    LocalisationReference = None

    def getText(self, id, value):
        return self.LocalisationReference.getText(self.name, value, Utils.getChannelLanguage(self.db, id))

    def getDescription(self, channelID):
        return self.LocalisationReference.getText(self.name, "description", Utils.getChannelLanguage(self.db, channelID))
    
    def getAdditionalUserValues(self):
        return None
    def getAdditionalGuildvalues(self):
        return None

    def GiveDataBaseReference(self, db):
        self.db = db

    def getUpdateFunctions(self):
        return None

    def getCommands(self):
        return None

    def getAdditionalGuildValues(self):
        return None

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
    async def on_webhoooks_update(self, channel):
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