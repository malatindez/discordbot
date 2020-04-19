
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import platform
class Song:
    def __init__(self, data):
        print(data)
        for key in data.keys():
            setattr(self, key, data[key])
    def __str__(self):
        return """
filepath: {}
Title: {}
TC id: {}
User id: {}
Track: {}
Alt title: {}
Artist: {}
Channel: {}
Video id: {}
Duration: {}
""".format(self.filepath, self.title, self.TextChannelID,
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

    def __init__(self, enqueuedby):
        self.repeat = False
        self.shuffle = 0
        self.enqueuedby = enqueuedby
        if platform.system() == "Linux":
            self.template = Image.open("BotPackages/music/template.png")
            self.pause_gray = Image.open("BotPackages/music/pause_gray.png")
            self.play_gray = Image.open("BotPackages/music/play_gray.png")
            self.repeat_gray = Image.open("BotPackages/music/repeat_gray.png")
            self.repeat_one = Image.open("BotPackages/music/repeat_one.png")
            self.repeat_all = Image.open("BotPackages/music/repeat_all.png")
            self.shuffle_gray = Image.open("BotPackages/music/shuffle_gray.png")
            self.shuffle_white = Image.open("BotPackages/music/shuffle_white.png")
            self.font12 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 12)
            self.font16 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 16)
            self.font24 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 24)
            self.font36 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 36)
            self.font48 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 48)
            self.font64 = ImageFont.truetype(r"BotPackages/music/LeelawUI.ttf", 64)
        elif platform.system() == "Windows":
            self.template = Image.open("BotPackages\\music\\template.png")
            self.pause_gray = Image.open("BotPackages\\music\\pause_gray.png")
            self.play_gray = Image.open("BotPackages\\music\\play_gray.png")
            self.repeat_gray = Image.open("BotPackages\\music\\repeat_gray.png")
            self.repeat_one = Image.open("BotPackages\\music\\repeat_one.png")
            self.repeat_all = Image.open("BotPackages\\music\\repeat_all.png")
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
        self.curr_page = 0
        self.queue = [None]
        self.curr_repeat = False
        self.update_flag = False
        self.paused = False
        self.page = 0
        self.update()
    @staticmethod
    def getSongTitleAndAuthor(song):
        title = song.title
        author = song.channel
        flag = False
        if song.artist is not None:
            author = song.artist
            flag = True
        if song.track is not None:
            title = song.track
            flag = True
        else:
            flag = False
        if not flag:
            if '-' in title:
                channel = title[:title.find('-')]
                title = title[title.find('-') + 2:]
        return (title, author)
    @staticmethod
    def bettertime(duration):
        x = [int(duration / 60), duration % 60]
        for i in range(2):
            if x[i] >= 10:
                x[i] = str(x[i])
            else:
                x[i] = "0" + str(x[i])
        return "{x[0]}:{x[1]}".format(x=x)
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
        if self.page != self.curr_page:
            self.curr_page = self.page
            if not copied:
                self.curr_img = Image.new('RGBA', self.template.size, (0, 0, 0, 0))
                self.curr_img.paste(self.template, (0,0))
                copied = True
        if copied:
            if self.repeat == 0:
                self.curr_img.paste(self.repeat_gray, (799, 1), mask=self.repeat_gray)
            elif self.repeat == 1:
                self.curr_img.paste(self.repeat_one, (799, 1), mask=self.repeat_one)
            elif self.repeat == 2:
                self.curr_img.paste(self.repeat_all, (799, 1), mask=self.repeat_all)
            if self.shuffle == 0:
                self.curr_img.paste(self.shuffle_gray, (640, 1), mask=self.shuffle_gray)
            elif self.shuffle == 1:
                self.curr_img.paste(self.shuffle_white, (640, 1), mask=self.shuffle_white)
                
            if self.queue[0] is None or self.paused:
                self.curr_img.paste(self.play_gray, (31, 1), mask = self.play_gray)
            else:
                self.curr_img.paste(self.pause_gray, (31, 1), mask = self.pause_gray)
            if self.queue[0] is not None:
                for i in self.queue:
                    if not hasattr(i, 'img'):
                        i.img = self.downloadAndCreateImage(i.video_id)
                self.curr_img.paste(self.cropAndResize(self.queue[0].img, (400, 400)), (26, 137))

                draw = ImageDraw.Draw(self.curr_img)
                draw.text((970, 705), 
                          "{0} - {1} / {2}".format(1 + self.page * 7, 7 + self.page * 7, len(self.queue) - 1),
                         fill = (170, 170, 170),
                        font=self.font36)
                title0, author0 = self.getSongTitleAndAuthor(self.queue[0])
                if len(title0) > 30:
                    draw.text((472, 165), title0, fill = (170, 170, 170), font=self.font16)
                elif len(title0) > 20:
                    draw.text((472, 158), title0, fill = (170, 170, 170), font=self.font24)
                else:
                    draw.text((472, 140), title0, fill = (170, 170, 170), font=self.font48)
                if len(author0) > 30:
                    draw.text((598, 270), author0, fill = (170, 170, 170), font=self.font16)
                elif len(author0) > 12:
                    draw.text((598, 268), author0, fill = (170, 170, 170), font=self.font24)
                else:
                    draw.text((598, 252), author0, fill = (170, 170, 170), font=self.font48)
                draw.text((764, 354), self.bettertime(self.queue[0].duration), fill = (170, 170, 170), font=self.font64)
                draw.text((470, 480), self.enqueuedby, fill = (170, 170, 170), font=self.font48)
                draw.text((610, 590), self.queue[0].user, fill = (170, 170, 170), font=self.font36)
                for i in range(1 + self.page * 7, len(self.queue)):
                    if i == 1 + (self.page+1) * 7:
                        break
                    self.curr_img.paste(self.cropAndResize(self.queue[i].img, (80, 80)), (962, 57 + (i - self.page * 7) * 80))
                    title, author = self.getSongTitleAndAuthor(self.queue[i])
                    if len(title) > 36:
                        draw.text((1060, 65 + (i - self.page * 7) * 80), title, fill = (170, 170, 170), font=self.font12)
                    elif len(title) > 20:
                        draw.text((1060, 65 + (i - self.page * 7) * 80), title, fill = (170, 170, 170), font=self.font16)
                    else:
                        draw.text((1060, 56 + (i - self.page * 7) * 80), title, fill = (170, 170, 170), font=self.font24)
                    if len(author) > 20:
                        draw.text((1060, 95 + (i - self.page * 7) * 80), author, fill = (170, 170, 170), font=self.font16)
                    else:
                        draw.text((1060, 91 + (i - self.page * 7) * 80), author, fill = (170, 170, 170), font=self.font24)
        if copied:
            self.curr_img_queue = self.queue.copy()
            self.curr_img.save('tmpMusic.png')
            self.update_flag = True
    def next(self):
        song = None
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
                rand = 0
                if len(self.queue) > 1:
                    rand = randint(1, len(self.queue)-1)
                elif len(self.queue) > 4:
                    rand = randint(1, len(self.queue)-2)
                elif len(self.queue) > 8:
                    rand = randint(1, len(self.queue)-4)
                song = self.queue[rand]
                self.queue.remove(self.queue[rand])
                self.queue.insert(1, song)
                buf = self.queue[0]
                self.queue.remove(self.queue[0])
                self.append(buf)
            elif len(self.queue) > 1:
                song = self.queue[1]
                buf = self.queue[0]
                self.queue.remove(self.queue[0])
                self.append(buf)
            else:
                song = self.queue[0]
        if song == None:
            self.queue = [None]
        return song



    def __len__(self):
        return len(self.queue)

    def append(self, song):
        self.queue.append(song)