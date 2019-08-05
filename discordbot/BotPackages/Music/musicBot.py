import discord
import asyncio

def f():
    while True:
        print("123")
async def update():
    while True:
        asyncio.sleep(0.025)
def INIT_UPDATE(token, pipe):
    client = discord.Client()
    client.loop.create_task(update())
    client.run(self.token)