
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

class Song:
    def __init__(self, data, data2 = {}):
        print(data)
        for key in data[0].keys():
            setattr(self, key, data[0][key])
        for key in data[1].keys():
            setattr(self, key, data[1][key])
    def __str__(self):
        return """
filepath: {}
Title: {}
TC id: {}
Now_playing string: {}
User id: {}
Track: {}
Alt title: {}
Artist: {}
Channel: {}
Video id: {}
Duration: {}
""".format(self.filepath, self.title, self.TextChannelID, self.play,
           self.userid, self.track, self.alt_title, self.artist,
           self.channel, self.video_id, self.duration)
from random import randint
class SongQueue:
    
    @staticmethod
    def downloadAndCreateImage(video_id):
        return Image.open(BytesIO(
            requests.get('https://i.ytimg.com/vi/{}/sddefault.jpg'.format(video_id)).content
            ))
    @staticmethod
    def cropAndResize(im_ref, size):
        im = im_ref.crop((140, 60, 500, 420))
        im.load()
        x, y = size
        if x > 360 or y > 360:
            im = im.resize(size)
        else:
            im.thumbnail(size, Image.ANTIALIAS)
        return im

    def __init__(self):
        self.repeat = False
        self.shuffle = 0
        self.template = Image.open("BotPackages\\music\\template.png")
        self.pause_gray = Image.open("BotPackages\\music\\pause_gray.png")
        self.play_gray = Image.open("BotPackages\\music\\play_gray.png")
        self.repeat_gray = Image.open("BotPackages\\music\\repeat_gray.png")
        self.repeat_white = Image.open("BotPackages\\music\\repeat_white.png")
        self.repeat_red = Image.open("BotPackages\\music\\repeat_red.png")
        self.shuffle_gray = Image.open("BotPackages\\music\\shuffle_gray.png")
        self.shuffle_white = Image.open("BotPackages\\music\\shuffle_white.png")
        self.font12 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 12)
        self.font16 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 16)
        self.font24 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 24)
        self.font36 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 36)
        self.font48 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 48)
        self.font64 = ImageFont.truetype(r"BotPackages\\music\\LeelawUI.ttf", 64)
        self.curr_img = self.template.copy()
        self.curr_img_queue = []
        self.curr_shuffle = 0
        self.curr_repeat = False
        self.queue = [None]
        self.curr_repeat = False
        self.update_flag = False
        self.paused = False
        self.update()
    def update(self):
        copied = False
        flag = len(self.curr_img_queue) != len(self.queue)
        if not flag:
            for i in range(len(self.curr_img_queue)):
                if self.curr_img_queue[i] != self.queue[i]:
                    flag = True
                    break
        if flag:
            copied = True
            self.curr_img = Image.new('RGBA', self.template.size, (0, 0, 0, 0))
            self.curr_img.paste(self.template, (0,0))
        if self.shuffle != self.curr_shuffle:
            self.curr_shuffle = self.shuffle
            if not copied:
                self.curr_img = Image.new('RGBA', self.template.size, (0, 0, 0, 0))
                self.curr_img.paste(self.template, (0,0))
                copied = True
        if self.repeat != self.curr_repeat:
            self.curr_repeat = self.repeat
            if not copied:
                self.curr_img = Image.new('RGBA', self.template.size, (0, 0, 0, 0))
                self.curr_img.paste(self.template, (0,0))
                copied = True

        if copied:
            if self.repeat == 0:
                self.curr_img.paste(self.repeat_gray, (799, 682), mask=self.repeat_gray)
            elif self.repeat == 1:
                self.curr_img.paste(self.repeat_white, (799, 682), mask=self.repeat_white)
            elif self.repeat == 2:
                self.curr_img.paste(self.repeat_red, (799, 682), mask=self.repeat_red)
            print(self.shuffle)
            if self.shuffle == 0:
                self.curr_img.paste(self.shuffle_gray, (640, 682), mask=self.shuffle_gray)
            elif self.shuffle == 1:
                self.curr_img.paste(self.shuffle_white, (640, 682), mask=self.shuffle_white)
                
            if self.queue[0] is None or self.paused:
                self.curr_img.paste(self.pause_gray, (191, 682), mask = self.pause_gray)
            else:
                self.curr_img.paste(self.play_gray, (191, 682), mask = self.play_gray)


            if self.queue[0] is not None:
                for i in self.queue:
                    if not hasattr(i, 'img'):
                        i.img = self.downloadAndCreateImage(i.video_id)
                self.curr_img.paste(self.cropAndResize(self.queue[0].img, (400, 400)), (29, 61))

                draw = ImageDraw.Draw(self.curr_img)
                for i in range(1, len(self.queue)):
                    print(self.queue)
                    if i == 8:
                        break
                    self.curr_img.paste(self.cropAndResize(self.queue[i].img, (80, 80)), (966, -19 + i * 80))
                    title = self.queue[i].title
                    author = self.queue[i].channel
                    print(title)
                    print(author)
                    print(self.queue[i].artist)
                    print(self.queue[i].track)
                    flag = False
                    if self.queue[i].artist is not None:
                        author = self.queue[i].artist
                        flag = True
                    if self.queue[i].track is not None:
                        title = self.queue[i].track
                        flag = True
                    else:
                        flag = False
                    if not flag:
                        if '-' in title:
                            channel = title[:title.find('-')]
                            title = title[title.find('-') + 2:]
                    if len(title) > 36:
                        draw.text((1060, -7 + i * 80), title, fill = (170, 170, 170), font=self.font12)
                    elif len(title) > 20:
                        draw.text((1060, -7 + i * 80), title, fill = (170, 170, 170), font=self.font16)
                    else:
                        draw.text((1060, -15 + i * 80), title, fill = (170, 170, 170), font=self.font24)
                    if len(author) > 20:
                        draw.text((1060, 22 + i * 80), author, fill = (170, 170, 170), font=self.font16)
                    else:
                        draw.text((1060, 18 + i * 80), author, fill = (170, 170, 170), font=self.font24)
        if copied:
            self.curr_img_queue = self.queue.copy()
            self.curr_img.save('tmpMusic.png')
            self.update_flag = True
    def next(self):
        song = None
        print(self.queue)
        if self.repeat == 0:
            if self.shuffle:
                rand = randint(1 , len(self.queue))
                song = self.queue[rand]
                self.queue.remove(self.queue[rand])
                self.queue.insert(1, song)
            else:
                if len(self.queue) > 1:
                    self.queue.remove(self.queue[0])
                    song = self.queue[0]
                    print(song)
        elif self.repeat == 1:
            song = self.queue[0]
        elif self.repeat == 2:
            if self.shuffle:
                rand = randint(1, len(self.queue)-1)
                if len(self.queue) >= 4:
                    rand = randint(1, len(self.queue)-2)
                elif len(self.queue) >= 8:
                    rand = randint(1, len(self.queue)-4)
                song = self.queue[rand]
                self.queue.remove(self.queue[rand])
                self.queue.insert(1, song)
            else:
                song = self.queue[1]
            buf = self.queue[0]
            self.queue.remove(self.queue[0])
            self.append(buf)
        return song



    def __len__(self):
        return len(self.queue)

    def append(self, song):
        self.queue.append(song)