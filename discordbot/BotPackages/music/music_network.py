
class Package:
    available_types = [str, int, bool]
    def __getitem__(self, index):
        return self.data[index]
    @staticmethod #data - list
    def create(code, data, salt = 0, typep = 0):
        req = Package()
        if not isinstance(code, int):
            raise ValueError
        if not isinstance(salt, int):
            raise ValueError
        if not isinstance(typep, int):
            raise ValueError
        for i in data:
            if type(i) not in Package.available_types:
                raise ValueError
        req.code = code
        req.data = data
        req.salt = salt
        req.type = typep
        return req

    def to_bytes(self):
        b = bytearray()
        b.extend(self.code.to_bytes(2, byteorder='big'))
        b.extend(self.salt.to_bytes(2, byteorder='big'))
        b.extend(self.type.to_bytes(1, byteorder='big'))
        for var in self.data:
            if type(var) == int:
                b.extend((252).to_bytes(1,byteorder='big'))
                b.extend(var.to_bytes(8,byteorder='big'))

            elif type(var) == bool:
                b.extend((253).to_bytes(1,byteorder='big'))
                b.extend(var.to_bytes(1,byteorder='big'))

            elif type(var) == str:
                b.extend((254).to_bytes(1,byteorder='big'))
                encoded = var.encode('utf-8')
                b.extend(len(encoded).to_bytes(2,byteorder='big'))
                b.extend(encoded)
        b.extend((255).to_bytes(1,byteorder='big'))
        return b
    @staticmethod
    def from_bytes(connRef):
        x = Package()
        data = bytearray()
        code = connRef.recv(2)
        data.extend(code)
        x.code = int.from_bytes(code,byteorder='big')
        salt = connRef.recv(2)
        data.extend(salt)
        x.salt = int.from_bytes(salt,byteorder='big')
        type = connRef.recv(1)
        data.extend(type)
        x.type = int.from_bytes(type,byteorder='big')
        x.data = []
        while True:
            tb = connRef.recv(1)
            data.extend(tb)
            type = int.from_bytes(tb, byteorder='big')
            if type == 252: # int
                integer = connRef.recv(8)
                data.extend(integer)
                x.data.append(int.from_bytes(integer, byteorder='big'))
            elif type == 253: # bool
                boolean = connRef.recv(1)
                data.extend(boolean)
                x.data.append(bool.from_bytes(boolean, byteorder='big'))
            elif type == 254: # str
                lenstring = connRef.recv(2)
                data.extend(lenstring)
                lenstr = int.from_bytes(lenstring, byteorder='big')
                string = connRef.recv(lenstr)
                data.extend(string)
                x.data.append(string.decode('utf-8'))
            elif type == 255:
                break
            else:
                print(data)
                raise ValueError
        return x
    def __str__(self):
        return "code: {}, type: {}, data: {}".format(self.code, self.type, self.data)
from threading import Thread
import asyncio
from random import randint
import time
class bconn:
    def __init__(self, conn):
        self.conn = conn
        self.callbacks = []
        self.salts = []
        self.get_responses = {}
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.update())
        self.loop_thread = Thread(target=self.loop.run_forever,args=())
        self.loop_thread.start()
    def __del__(self):
        self.loop.stop()

    # async def func(data)
    # those funcs must use locks
    # and return response data if they're GET
    def createCallback(self, func, code):
        self.callbacks.append((func, code))

    # POST, TYPE = 0
    def POST(self, code, data):
        self.conn.send(Package.create(code,data).to_bytes())
    
    # GET, TYPE = 1
    def GET(self, code, data):
        salt = randint(1,65535)
        while salt in self.salts:
            salt = randint(1,65535)
        self.salts.append(salt)
        pckg = Package.create(code,data,salt, 1)
        self.conn.send(pckg.to_bytes())
        while True:
            time.sleep(0.25)
            if salt in self.get_responses:
                v = self.get_responses[salt]
                del self.get_responses[salt]
                self.salts.remove(salt)
                return v

    # GET_RESPONSE, TYPE = 2
    async def update(self):
        while True:
            r = Package.from_bytes(self.conn)
            print(r)

            if r.type == 2:
                self.get_responses.update({r.salt:r.data})
            elif r.type == 1:
                flag = False
                for callback, code in self.callbacks:
                    if code == r.code:
                        response = await callback(r.data)
                        self.conn.send(Package.create(code, response, r.salt, 2).to_bytes())
                        flag = True
                        break
                if not flag:
                    self.conn.send(Package.create(r.code, [], r.salt, 2).to_bytes())
            elif r.type == 0:
                for callback, code in self.callbacks:
                    if code == r.code:
                        await callback(r.data)