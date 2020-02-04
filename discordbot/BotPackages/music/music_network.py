
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
                id = (254-self.available_types.index(t))
                if t == int == type(var):
                    b.extend(id.to_bytes(1,byteorder='big'))
                    b.extend(var.to_bytes(8,byteorder='big'))
                    break
                elif t == type(var) == bool:
                    b.extend(id.to_bytes(1,byteorder='big'))
                    b.extend(var.to_bytes(1,byteorder='big'))
                    break
                elif t == type(var) == str:
                    b.extend(id.to_bytes(1,byteorder='big'))
                    encoded = var.encode('utf-8')
                    b.extend(len(encoded).to_bytes(2,byteorder='big'))
                    b.extend(encoded)
                    break
                elif t == type(var):
                    b.extend(id.to_bytes(1,byteorder='big'))
                    val = var.to_bytes()
                    b.extend(len(val).to_bytes(2,byteorder='big'))
                    b.extend(val)
                    
        b.extend((255).to_bytes(1,byteorder='big'))
        return b
    def __str__(self):
        return "code: {}, type: {}, data: {}".format(self.code, self.type, self.data)
class PackageCreator:
    # additional_types - list of types,
    # each type must have to_bytes() and static from_bytes(bytearray) functions
    def __init__(self, additional_types):
        self.available_types.extend(additional_types)
    available_types = [int, bool, str]
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
            if type(i) not in self.available_types:
                raise ValueError
        req.code = code
        req.data = data
        req.salt = salt
        req.type = typep
        return req

    def from_bytes(self, connRef):
        x = Package()
        data = bytearray()
        print("waiting for data")
        code = connRef.recv(2)
        data.extend(code)
        print(data)
        x.code = int.from_bytes(code,byteorder='big')
        salt = connRef.recv(2)
        data.extend(salt)
        print(data)
        x.salt = int.from_bytes(salt,byteorder='big')
        type = connRef.recv(1)
        data.extend(type)
        print(data)
        x.type = int.from_bytes(type,byteorder='big')
        x.data = []
        while True:
            tb = connRef.recv(1)
            data.extend(tb)
            print(data)
            type = 254 - int.from_bytes(tb, byteorder='big')
            print(type)
            print(self.available_types[type])
            if type == -1:
                break
            if type > len(self.available_types):
                raise ValueError
            if self.available_types[type] == int: # int
                integer = connRef.recv(8)
                data.extend(integer)
                x.data.append(int.from_bytes(integer, byteorder='big'))
            elif self.available_types[type] == bool: # bool
                boolean = connRef.recv(1)
                data.extend(boolean)
                x.data.append(bool.from_bytes(boolean, byteorder='big'))
            elif self.available_types[type] == str: # str
                lenstring = connRef.recv(2)
                data.extend(lenstring)
                lenstr = int.from_bytes(lenstring, byteorder='big')
                string = connRef.recv(lenstr)
                data.extend(string)
                x.data.append(string.decode('utf-8'))
            else:
                datalen = connRef.recv(2)
                data.extend(datalen)
                lenstr = int.from_bytes(datalen, byteorder='big')
                recvdata = connRef.recv(lenstr)
                data.extend(recvdata)
                x.data.append(self.available_types[type].from_bytes(recvdata))
        print(data)
        print(x)
        return x
from threading import Thread
import asyncio
from random import randint
import time
class bconn:
    
    def __init__(self, conn, additional_types = [], callbacks = []):
        self.pc = PackageCreator(additional_types)
        self.conn = conn
        self.callbacks = callbacks
        self.salts = []
        self.get_responses = {}
        self.loop = asyncio.new_event_loop()
        self.loop.create_task(self.update())
        self.loop_thread = Thread(target=self.loop.run_forever,args=())
        self.loop_thread.start()
    def __del__(self):
        self.loop.stop()

    # async def func(data, conn)
    # those funcs must use locks
    # and return response data if they're GET
    def createCallback(self, func, code):
        self.callbacks.append((func, code))

    # POST, TYPE = 0
    def POST(self, code, data):
        self.conn.send(self.pc.create(code,data).to_bytes())
    
    # GET, TYPE = 1
    async def GET(self, code, data, delay = 0.25):
        salt = randint(1,65535)
        while salt in self.salts:
            salt = randint(1,65535)
        self.salts.append(salt)
        pckg = self.pc.create(code,data,salt, 1)
        self.conn.send(pckg.to_bytes())
        print(data)
        while True:
            await asyncio.sleep(delay)
            if salt in self.get_responses:
                v = self.get_responses[salt]
                del self.get_responses[salt]
                self.salts.remove(salt)
                return v

    # GET_RESPONSE, TYPE = 2
    async def update(self):
        while True:
            print('update')
            r = self.pc.from_bytes(self.conn)
            print(r)

            if r.type == 2:
                self.get_responses.update({r.salt:r.data})
            elif r.type == 1:
                flag = False
                for callback, code in self.callbacks:
                    if code == r.code:
                        response = await callback(r.data, self)
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
                        await callback(r.data, self)