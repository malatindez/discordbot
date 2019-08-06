import sys
import time
import asyncio
import os
import discord
import pipes
import platform
import multiprocessing as mp
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/Music")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\Music")
import Utils
import Package as pckg
import musicBot as mb
class Package(pckg.Package):

    name = "music"
    bots = []
    def __init__(self, LocalisationReference):
        self.LocalisationReference = LocalisationReference
        if platform.system() == "Windows":
            print("Music package cannot be loaded on Windows")
            return
        tokens = []
        if platform.system() == "Linux":
            f = open(os.path.dirname(os.path.realpath(__file__)) + "/../../musictokens")
            for token in f:
                tokens.append(token.replace("\n", ""))
        elif platform.system() == "Windows":
            f = open(os.path.dirname(os.path.realpath(__file__)) + "\\..\\..\\musictokens")
            for token in f:
                tokens.append(token.replace("\n", ""))
        for token in tokens:
            parentPipe, childPipe = mp.Pipe()
            p = mp.Process(target=mb.INIT_UPDATE, args=(token, childPipe, ))
            p.start()
            self.bots.append([p, parentPipe])
    def getCommands(self):
        return [["help", self.help]]

    async def help(self, params, message, client):
        pass