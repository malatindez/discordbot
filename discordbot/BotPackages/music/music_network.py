import json
class Package:
    def __getitem__(self, index):
        return self.data[index]
    def to_bytes(self):
        b = bytearray()
        b.extend(self.code.to_bytes(2, byteorder='big'))
        b.extend(self.salt.to_bytes(2, byteorder='big'))
        b.extend(self.type.to_bytes(1, byteorder='big'))
        for var in self.data:
            for t in self.available_types:
                def saveBytes(encoded):
                    b.extend(len(encoded).to_bytes(2,byteorder='big'))
                    b.extend(encoded)
                id = (254-self.available_types.index(t))
                if t == type(var):
                    b.extend(id.to_bytes(1,byteorder='big'))
                    if t == int:
                        b.extend(var.to_bytes(8,byteorder='big'))
                    elif t == bool:
                        b.extend(var.to_bytes(1,byteorder='big'))
                    elif t == str:
                        saveBytes(var.encode('utf-8'))
                    elif t == dict or t == list:
                        saveBytes(json.dumps(var).encode('utf-8'))
                    else:
                        saveBytes(var.to_bytes())
                    break
        b.extend((255).to_bytes(1,byteorder='big'))
        return b
    def __str__(self):
        return "code: {}, type: {}, data: {}".format(self.code, self.type, self.data)
class PackageCreator:
    # additional_types - list of types,
    # each type must have to_bytes() and static from_bytes(bytearray) functions
    def __init__(self, additional_types):
        self.available_types.extend(additional_types)
    available_types = [int, bool, str, dict, list]
    def create(self, code, data, salt = 0, typep = 0):
        req = Package()
        req.available_types = self.available_types
        if not isinstance(code, int):
            raise ValueError
        if not isinstance(salt, int):
            raise ValueError
        if not isinstance(typep, int):
            raise ValueError
        for i in data:
            if i is None:
                data[data.index(i)] = 0
            elif type(i) not in self.available_types:
                raise ValueError
        req.code = code
        req.data = data
        req.salt = salt
        req.type = typep
        return req

    async def from_bytes(self, connRef):
        x = Package()
        data = bytearray()
        code = await asyncio.get_event_loop().sock_recv(connRef, 2)
        x.code = int.from_bytes(code,byteorder='big')
        salt = await asyncio.get_event_loop().sock_recv(connRef, 2)
        x.salt = int.from_bytes(salt,byteorder='big')
        type = await asyncio.get_event_loop().sock_recv(connRef, 1)
        x.type = int.from_bytes(type,byteorder='big')
        x.data = []
        async def getData():
            lenstring = await asyncio.get_event_loop().sock_recv(connRef, 2)
            lenstr = int.from_bytes(lenstring, byteorder='big')
            returnData = await asyncio.get_event_loop().sock_recv(connRef, lenstr)
            return returnData
        while True:
            tb = await asyncio.get_event_loop().sock_recv(connRef, 1)
            data.extend(tb)
            type = 254 - int.from_bytes(tb, byteorder='big')
            if type == -1:
                break
            if type > len(self.available_types):
                raise ValueError
            if self.available_types[type] == int:
                integer = await asyncio.get_event_loop().sock_recv(connRef, 8)
                x.data.append(int.from_bytes(integer, byteorder='big'))
            elif self.available_types[type] == bool:
                boolean = await asyncio.get_event_loop().sock_recv(connRef, 1)
                x.data.append(bool.from_bytes(boolean, byteorder='big'))
            elif self.available_types[type] == str:
                x.data.append((await getData()).decode('utf-8'))
            elif self.available_types[type] == dict or self.available_types[type] == list:
                x.data.append(json.loads((await getData()).decode('utf-8')))
            else:
                recvdata = await getData()
                x.data.append(self.available_types[type].from_bytes(recvdata))
        return x
from threading import Thread
import asyncio
from random import randint
from time import time
class bconn:
    dead = False
    def __init__(self, loop, conn, additional_types = [], callbacks = []):
        self.pc = PackageCreator(additional_types)
        self.conn = conn
        self.callbacks = callbacks
        self.salts = []
        self.get_responses = {}
        loop.create_task(self.update())

    # async def func(data, conn)
    # those funcs must use locks
    # and return response data if they're GET
    def createCallback(self, func, code):
        self.callbacks.append((func, code))

    # POST, TYPE = 0
    def POST(self, code, data):
        self.conn.send(self.pc.create(code,data).to_bytes())
    
    # GET, TYPE = 1
    async def GET(self, code, data, delay = 0.25, timeout = 60):
        salt = randint(1,65535)
        while salt in self.salts:
            salt = randint(1,65535)
        self.salts.append(salt)
        pckg = self.pc.create(code,data,salt, 1)
        self.conn.send(pckg.to_bytes())
        t = time()
        while True:
            if time() - t > timeout:
                print("timeout!")
                return []
            await asyncio.sleep(delay)
            if salt in self.get_responses:
                v = self.get_responses[salt]
                del self.get_responses[salt]
                self.salts.remove(salt)
                return v
            if self.dead:
                return []

    # GET_RESPONSE, TYPE = 2
    async def update(self):
        while True:
            try:
                r = await self.pc.from_bytes(self.conn)

                if r.type == 2:
                    self.get_responses.update({r.salt:r.data})
                elif r.type == 1:
                    flag = False
                    for callback, code in self.callbacks:
                        if code == r.code:
                            response = None
                            try:
                                response = await callback(r.data, self)
                            except Exception as e:
                                print(str(e) + " Occured in musicNetwork")

                            if response is None:
                                response = []
                            self.conn.send(self.pc.create(code, response, r.salt, 2).to_bytes())
                            flag = True
                            break
                    if not flag:
                        self.conn.send(self.pc.create(r.code, [], r.salt, 2).to_bytes())
                elif r.type == 0:
                    for callback, code in self.callbacks:
                        if code == r.code:
                            try:
                                await callback(r.data, self)
                            except Exception as e:
                                print(str(e) + " Occured in musicNetwork")
            except Exception as e:
                print(e)
                self.dead = True
                return