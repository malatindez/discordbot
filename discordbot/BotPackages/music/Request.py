
class Request:
    available_types = [str, int, bool]
    def __getitem__(self, index):
        return self.data[index]
    @staticmethod #data - list
    def create(code, data):
        req = Request()
        if not isinstance(code, int):
            raise ValueError
        for i in data:
            if type(i) not in Request.available_types:
                raise ValueError
        req.code = code
        req.data = data
        return req

    def to_bytes(self):
        b = bytearray()
        b.extend(self.code.to_bytes(1, byteorder='big'))
        for var in self.data:
            if type(var) == int:
                b.extend((0).to_bytes(1,byteorder='big'))
                b.extend(var.to_bytes(8,byteorder='big'))

            elif type(var) == bool:
                b.extend((1).to_bytes(1,byteorder='big'))
                b.extend(var.to_bytes(1,byteorder='big'))

            elif type(var) == str:
                b.extend((2).to_bytes(1,byteorder='big'))
                encoded = var.encode('utf-8')
                b.extend(len(encoded).to_bytes(2,byteorder='big'))
                b.extend(encoded)
        b.extend((255).to_bytes(1,byteorder='big'))
        return b
    def from_bytes(self, data):
        self.code = int.from_bytes(data[0:1],byteorder='big')
        self.data = []
        indent = 1

        while indent < len(data):
            type = int.from_bytes(data[indent:indent + 1], byteorder='big')
            indent += 1
            if type == 0: # int
                self.data.append(int.from_bytes(data[indent:indent+8], byteorder='big'))
                indent += 8
            elif type == 1: # bool
                self.data.append(bool.from_bytes(data[indent:indent+1], byteorder='big'))
                indent += 1
            elif type == 2: # str
                lenstr = int.from_bytes(data[indent:indent + 2], byteorder='big')
                indent += 2
                self.data.append(data[indent:indent + lenstr].decode('utf-8'))
                indent += lenstr
            elif type == 255:
                break
            else:
                raise ValueError
