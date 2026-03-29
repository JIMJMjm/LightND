from datetime import datetime
from os.path import exists as ext
from os import listdir as ldr, mkdir, remove
from concurrent.futures import ThreadPoolExecutor

from winsound import PlaySound

from book_struct import HmzedBook, BankedBook, BookLuxury
from netwk import GetRq, get_fullinfo
import bookbank
from config import save_json, CONFIG, confirm_name, LANG, ordered_ldr

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/127.0.0.0 '
                        'Safari/537.36'}

MAX_WAORKERS = CONFIG["MAX_THREAD_WORKER"]
AUDD = CONFIG["ALWAYS_USE_DEFAULT_DOWNLOAD"]
IRST = CONFIG["ILLUSTRATION_REQUEST_SLEEP_TIME"]
TRST = CONFIG["TEXT_REQUEST_SLEEP_TIME"]
MAX_VOL_WORKERS = CONFIG["MAX_VOLUME_THREAD_WORKER"]
BANK_PATH = CONFIG["BANK_PATH"]


def makedir(fname):
    if ext(fname):
        return None
    mkdir(fname)
    return None


def get_img(numname, iis=False):
    if ext(f'images/thumbnails/{numname}.jpg'):
        return f'images/thumbnails/{numname}.jpg'
    url = f'https://img.wenku8.com/image/{int(numname) // 1000}/{numname}/{numname}s.jpg'
    m = GetRq(url).run('m')
    with open(f'images/thumbnails/{numname}.jpg', 'wb') as f:
        f.write(m)
    if iis:
        return f'images/thumbnails/{numname}.jpg'
    return m


def succeeded(info='Successful!'):
    print(info)
    PlaySound('dlcp.wav', 1)


def save_file(content, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return 0


def save_img(img: bytes, path):
    with open(path, 'wb') as f:
        f.write(img)
    return 0


class DownloadTask(object):
    def __init__(self, numname: str, state=2, mode=0, merging=False, g_dir=BANK_PATH,
                 update: bool | list[str] = False):
        if not numname:
            print('Not A Numname!')
            return

        if numname == '-2':
            print('Testing Task Object!')
            return

        self.state = state
        self.mode = mode
        self.merging = merging

        if update:
            self.rname = g_dir + '/' + update[1]
            self.numname = update[0]
            self.thisurl = f'https://www.wenku8.cc/novel/{int(update[0]) // 1000}/{update[0]}/'
            self.state = 0
            return

        self.numname = numname
        self.g_dir = g_dir

        modl = numname[0] if len(numname) > 3 else '0'
        self.thisurl = f'https://www.wenku8.cc/novel/{modl}/{numname}/'

        name, writer, descrp, genre, bunko, allnet, allname, cprt = get_fullinfo(numname, save=False)
        name = confirm_name(name)

        self.hmzbook = HmzedBook(numname=numname, name=name, writer=writer,
                                 allnet=allnet, allname=allname, description=descrp)

        self.bankbook = BankedBook(numname=numname, name=name, writer=writer,
                                   bunko=bunko, genre=genre, directory=g_dir,
                                   lux=BookLuxury(), addtime=datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        
        self.cprt = cprt
        self.rname = self.hmzbook.name
        if self.g_dir != '':
            self.rname = f'{g_dir}/{self.hmzbook.name}'

        self.__warning = None

        self.progress: int = 0

    def read_page(self, volumeName: str, url: str, fileIndex: int):
        text = GetRq(url).run('t')
        save_file(text, f'{self.rname}/{volumeName}/{fileIndex}.txt')
        return 1

    def illu_page(self, volumeName, url):
        dirnamr = f'{self.rname}/{volumeName}/插图'
        makedir(dirnamr)

        img_list = GetRq(url).run('f')
        for y, i in enumerate(img_list):
            save_img(i, f'{dirnamr}/{y + 1}.jpg')

        return 1

    def process_page(self, i: int, j: int, alllists=None):
        if alllists is None:
            allnet = self.hmzbook.allnet
            allname = self.hmzbook.name
        else:
            allnet = alllists[0]
            allname = alllists[1]
        url = self.thisurl + allnet[i][j]
        chapter_name = allname[i][j]
        volume_name = allname[i][0]

        if chapter_name == '插图':
            if self.state == 2:
                return 0
            return self.illu_page(volume_name, url)
        if self.state == 1:
            return 0
        return self.read_page(volume_name, url, j)

    def check_current_folder(self, adr, _type=-1):
        if _type == -1:
            volumes = [i[0] for i in self.hmzbook.allnet]
            for i in volumes:
                if i not in ldr(adr):
                    return max(volumes.index(i), 1)
        ord_ = ordered_ldr(adr)
        return len(ord_[0]) + ord_[1]

    def download_volume(self, volume: int):
        dirname = f'{self.rname}/{self.hmzbook.allnet[volume][0]}'
        makedir(dirname)

        with ThreadPoolExecutor(max_workers=MAX_WAORKERS) as executor:
            futures = []
            for j in range(1, len(self.hmzbook.allnet[volume])):
                future = executor.submit(self.process_page, volume, j)
                futures.append(future)

            for future in futures:
                future.result()
        return dirname

    def detailedDownload(self):
        makedir(self.rname)
        save_json(f'{self.rname}/{self.numname}.hmz',
                  {'name': self.hmzbook.name, 'writer': self.hmzbook.writer, 'allnet': self.hmzbook.allnet,
                   'allname': self.hmzbook.name, 'directory': self.g_dir, 'discription': self.hmzbook.description,
                   'genre': self.bankbook.genre, 'bunko': self.bankbook.bunko, 'numname': self.numname})

        start = self.check_current_folder(self.rname) - 1 if self.mode == 0 else 0
        for i in range(start, len(self.hmzbook.allnet)):
            dirname = self.download_volume(i)

            current_progress = i + 1 - start
            total_tasks = len(self.hmzbook.allnet) - start
            filled_length = int(30 * current_progress // total_tasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(current_progress / total_tasks) * 100:.2f}% ({current_progress}/{total_tasks})",
                  end='\r')

            if self.merging:
                self.mergeToVol(dirname, self.hmzbook.allnet[i][0])
        if self.merging == 2:
            self.mergeToSeries()
        print(LANG['DL_Finished'])

    def default_download(self):
        print('Using "Default Download"... No progress indicators.')
        makedir(self.rname)

        newurl = f'https://dl.wenku8.com/down.php?type=txt&node=2&id={self.numname}'
        tx = GetRq(newurl).run('w')

        save_file(tx, f'{self.rname}/{self.hmzbook.name}.txt')
        save_json(f'{self.rname}/{self.numname}.hmz',
                  {'name': self.hmzbook.name, 'writer': self.hmzbook.writer, 'allnet': self.hmzbook.allnet,
                   'allname': self.hmzbook.name, 'directory': self.g_dir, 'discription': self.hmzbook.description,
                   'genre': self.bankbook.genre, 'bunko': self.bankbook.bunko, 'numname': self.numname})

        print('Download Finished.')

    @staticmethod
    def mergeToVol(folder, output):
        file_all = ldr(folder)
        if file_all[-1][-4:] != '.txt':
            file_all.pop()

        out = f'{folder}/{output}.txt'
        if ext(out):
            remove(out)

        f = open(out, 'a', encoding='utf-8')
        for i in range(len(file_all)):
            if ext(fn := f'{folder}/{str(i + 1)}.txt'):
                adding = open(fn, encoding='utf-8')
                f.write(adding.read())
                f.write('\n')
        f.close()

    def mergeToSeries(self):
        out = f'{self.rname}/{self.hmzbook.name}.txt'
        if ext(out):
            remove(out)
        f = open(out, 'a', encoding='utf-8')
        for i in range(len(self.hmzbook.allnet)):
            if ext(fn := f'{self.rname}/{self.hmzbook.allnet[i][0]}/{self.hmzbook.allnet[i][0]}.txt'):
                adding = open(fn, encoding='utf-8')
                f.write(adding.read())
                f.write('\n')
        f.close()

    def txt_split(self):
        fileplace = f'{self.rname}/{self.hmzbook.name}.txt'
        with open(fileplace, 'r', encoding='utf-8') as f:
            content = f.readlines()[2:-2]
        true_content = [i.strip(' ') for i in content]

        intervals = []
        for i in self.hmzbook.name:
            for j in i[1:]:
                chapname = f'{i[0]} {j}'
                curind = content.index(chapname + '\n')
                content[curind] = ''
                intervals.append(curind)
                if j == '插图':
                    true_content[curind] = ''
                    true_content[curind + 1] = ''
                    intervals.pop()

        intervals.append(len(content))

        chapcnt = 0
        for i in self.hmzbook.name:
            filecount = 1
            setname = f'{self.rname}/{i[0]}'
            makedir(setname)
            cp_in_v = len(i) - 2 if '插图' in i else len(i) - 1
            for j in range(cp_in_v):
                save_file(''.join(true_content[intervals[chapcnt]:intervals[chapcnt + 1]]),
                          f'{setname}/{filecount}.txt')
                filecount += 1
                chapcnt += 1

    def download(self):
        if not ext(fn := f'images/thumbnails/{self.numname}.jpg'):
            tmr = GetRq(f'https://img.wenku8.com/image/{int(self.numname) // 1000}{f'/{self.numname}' * 2}s.jpg').run(
                'm')
            save_img(tmr, fn)
        addbankBool = bookbank.add_to_bank((self.numname, self.hmzbook.name, self.hmzbook.writer, self.bankbook.genre, self.bankbook.bunko))
        if addbankBool:
            self.__warning = 'ADDBANK'

        if not self.cprt:
            self.__warning = 'COPYRIGHT'
            self.default_download()
            self.txt_split()
            return None

        if AUDD:
            self.default_download()
            self.txt_split()
            if self.state != 2:
                self.get_image_from_vol()
            return None

        self.detailedDownload()
        return None

    def downloadslice(self, ind):
        if not ext(fn := f'images/thumbnails/{self.numname}.jpg'):
            tmr = GetRq(f'https://img.wenku8.com/image/{int(self.numname) // 1000}{f'/{self.numname}' * 2}s.jpg').run(
                'm')
            save_img(tmr, fn)
        addbankBool = bookbank.add_to_bank((self.numname, self.hmzbook.name, self.hmzbook.writer, self.bankbook.genre, self.bankbook.bunko))
        if addbankBool:
            self.__warning = 'ADDBANK'

        makedir(self.rname)
        save_json(f'{self.rname}/{self.numname}.hmz',
                  {'name': self.hmzbook.name, 'writer': self.hmzbook.writer, 'allnet': self.hmzbook.allnet,
                   'allname': self.hmzbook.name, 'directory': self.g_dir, 'discription': self.hmzbook.description,
                   'genre': self.bankbook.genre, 'bunko': self.bankbook.bunko, 'numname': self.numname})

        if not self.cprt:
            self.__warning = 'COPYRIGHT'
            self.default_download()
            self.txt_split()
            return 11

        if AUDD:
            self.default_download()
            self.txt_split()
            if self.state != 2:
                self.get_image_from_vol(ind)
            return 11

        partial_allnet = []
        for i in range(len(ind)):
            if ind[i]:
                partial_allnet.append(i)
        for y, i in enumerate(partial_allnet):
            current_progress = y + 1
            total_tasks = len(partial_allnet)
            filled_length = int(30 * current_progress // total_tasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(current_progress / total_tasks) * 100:.2f}% ({current_progress}/{total_tasks})",
                  end='\r')

            self.download_volume(i)
        print(LANG['DL_Finished'])
        return None

    def download_volumes_from_allnet(self, volnets, volnames):
        for y, vol in enumerate(volnets):
            curprogress = y + 1
            totaltasks = len(volnets)
            filled_length = int(30 * curprogress // totaltasks)
            bar = '=' * filled_length + ' ' * (30 - filled_length)
            print(f"DL: [{bar}] {(curprogress / totaltasks) * 100:.2f}% ({curprogress}/{totaltasks})", end='\r')

            dirname = f'{self.rname}/{vol[0]}'
            makedir(dirname)

            with ThreadPoolExecutor(max_workers=MAX_WAORKERS) as executor:
                futures = []
                for j in range(1, len(vol)):
                    future = executor.submit(self.process_page, y, j, (volnets, volnames))
                    futures.append(future)

                for future in futures:
                    future.result()
        hmz = get_fullinfo(self.numname, f'{self.rname}/{self.numname}.hmz')
        save_json(f'{self.rname}/{self.numname}.hmz', hmz)

        succeeded()

    def get_image_from_vol(self, slice_ind: None | list = None):
        if slice_ind is None:
            post_allname = self.hmzbook.name
            post_allnet = self.hmzbook.allnet
        else:
            post_allname = [self.hmzbook.name[i] for i in slice_ind if i]
            post_allnet = [self.hmzbook.allnet[i] for i in slice_ind if i]
        for vol in range(len(post_allname)):
            for a, b in zip(post_allnet[vol], post_allname[vol]):
                if b == '插图':
                    self.illu_page(post_allname[vol][0], self.thisurl + a)

    def getWarning(self):
        return self.__warning


def activate():
    a = GetRq('https://www.wenku8.cc/book/3917.htm')
    a.request(True)
    print(a.run('b'))


def activate2():
    allname = [
        [
            "第一卷 艾恩葛朗特",
            "一卷全",
            "插图"
        ],
        [
            "第二卷 艾恩葛朗特",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "后记",
            "插图"
        ],
        [
            "第三卷 妖精之舞",
            "序章",
            "第一章",
            "第二章",
            "第三章",
            "后记",
            "插图"
        ],
        [
            "第四卷 妖精之舞",
            "序章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "后记",
            "插图"
        ],
        [
            "第五卷 幽灵子弹",
            "序章",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "后记",
            "插图"
        ],
        [
            "第六卷 幽灵子弹",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "第十三章",
            "第十四章",
            "第十五章",
            "第十六章",
            "后记",
            "插图"
        ],
        [
            "第七卷 圣母圣咏",
            "序",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "后记",
            "插图"
        ],
        [
            "第八卷 Early and Late",
            "圈内事件",
            "圣剑",
            "起始之日",
            "后记",
            "插图"
        ],
        [
            "第九卷 Alicization Beginning",
            "序幕I 人界历三七二年七月",
            "序幕II 公元二〇二六年六月",
            "转章I",
            "第一章 UnderWorld 人界历三七八年三月",
            "后记",
            "插图"
        ],
        [
            "第十卷 Alicization Running",
            "第二章 Alicization计划 西元二〇二六年七月",
            "第三章 萨卡和亚剑术大会 人界历三七八年八月",
            "第四章 帝立修剑学院 人界历三八〇年三月",
            "转章Ⅱ",
            "后记",
            "插图"
        ],
        [
            "Progressive 1",
            "无星夜的咏叹调",
            "幕间 胡须的理由",
            "幻胧剑之回旋曲",
            "后记",
            "插图"
        ],
        [
            "第十一卷 Alicization Turning",
            "第五章 右眼的封印 人界历三八〇年五月",
            "转章Ⅲ",
            "第六章 囚犯与骑士 人界历三八〇年五月",
            "后记",
            "插图"
        ],
        [
            "第十二卷 Alicization Rising",
            "第七章 两名管理者 人界历三八〇年五月",
            "第八章 中央大教堂 人界历三八〇年五月",
            "后记",
            "插图"
        ],
        [
            "第十三卷 Alicization Dividing",
            "转章Ⅳ 西历二〇二六年七月六日",
            "第九章 整合骑士爱丽丝 人界历三八〇年五月",
            "第十章 整合骑土长贝尔库利 人界历三八〇年五月",
            "第十一章 元老院的秘密 人界历三八〇年五月",
            "后记",
            "插图"
        ],
        [
            "Progressive 2",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "后记",
            "插图"
        ],
        [
            "第十四卷 Alicization Uniting",
            "序章",
            "第十二章 最高祭司Administrator 人界历三八〇年五月",
            "第十三章 决战 人界历三八〇年五月",
            "后记",
            "插图"
        ],
        [
            "第十五卷 Alicization Invading",
            "第十四章 盗魂者（Subtilizer）西历二〇二六年六月～七月",
            "第十五章 于北方之地 人界历三八〇年十月",
            "第十六章 袭击Ocean Turtle 西元二〇二六年七月",
            "第十七章 黑暗领域 人界历三八〇年十一月",
            "后记",
            "插图"
        ],
        [
            "Progressive 3",
            "序",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "后记",
            "插图"
        ],
        [
            "官方同人志 Material Edition",
            "ME04 冰冷的手，温暖的心",
            "ME05 鼠尾草",
            "ME06 阿尔格特的决斗",
            "番外 唯一的究极手段",
            "ME10 16.6",
            "ME11 16.7",
            "ME12 16.8",
            "ME13 16.9",
            "ME14 Sugary Days 5",
            "ME14 Sugary Days 6"
        ],
        [
            "第十六卷 Alicization Exploding",
            "第十八章 地底世界大战 人界历三八〇年十一月七日 午后六点",
            "第十九章 光之巫女 人界历三八〇年十一月七日 午后八点",
            "后记",
            "插图"
        ],
        [
            "Progressive 4",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "后记",
            "插图"
        ],
        [
            "第十七卷 Alicization Awakening",
            "第二十章 各自的战斗 西历二〇二六年七月七日/人界历三八〇年十一月七日",
            "第二十一章 觉醒 西历二〇二六年七月七日/人界历三八〇年十一月七日",
            "后记",
            "插图"
        ],
        [
            "第十八卷 Alicization Lasting",
            "第二十一章 觉醒（承前）",
            "第二十二章 决战",
            "第二十三章 回归",
            "终幕 西元二〇二六年八月",
            "序幕Ⅲ",
            "后记",
            "插图"
        ],
        [
            "第十九卷 Moon Cradle",
            "序",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "后记",
            "插图"
        ],
        [
            "第二十卷 Moon Cradle",
            "序",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "后记",
            "插图"
        ],
        [
            "Progressive 5",
            "黄金定律的卡农 序",
            "黄金定律的卡农 1",
            "黄金定律的卡农 2",
            "黄金定律的卡农 3",
            "黄金定律的卡农 4",
            "黄金定律的卡农 5",
            "后记",
            "插图"
        ],
        [
            "第二十一卷 Unital Ring I",
            "序",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "后记",
            "插图"
        ],
        [
            "Progressive 6",
            "黄金定律的卡农 6",
            "黄金定律的卡农 7",
            "黄金定律的卡农 8",
            "黄金定律的卡农 9",
            "黄金定律的卡农 10",
            "黄金定律的卡农 11",
            "黄金定律的卡农 12",
            "黄金定律的卡农 13",
            "黄金定律的卡农 14",
            "黄金定律的卡农 15",
            "后记",
            "插图"
        ],
        [
            "第二十二卷 Kiss And Fly",
            "The day before",
            "The day after",
            "彩虹桥",
            "Sisters’ Prayer",
            "后记",
            "插图"
        ],
        [
            "第二十三卷 Unital Ring II",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "后记",
            "插图"
        ],
        [
            "第二十四卷 Unital Ring III",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "后记",
            "插图"
        ],
        [
            "第二十五卷 Unital Ring IV",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "后记",
            "插图"
        ],
        [
            "Progressive 7 赤色焦热的狂想曲 上",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "第十三章",
            "后记",
            "插图"
        ],
        [
            "BD特典小说 UW篇 IF线",
            "If You Were Here",
            "If You Wish It",
            "If We Could Walk Together"
        ],
        [
            "第二十六卷 Unital Ring V",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "第十三章",
            "第十四章",
            "第十五章",
            "第十六章",
            "第十七章",
            "第十八章",
            "第十九章",
            "第二十章",
            "第二十一章",
            "第二十二章",
            "第二十三章",
            "后记",
            "插图"
        ],
        [
            "短篇",
            "温泉篇",
            "天青色的妖精",
            "LISBETH EDITION 水之音，锤之音",
            "SILICA EDITION 冬日暖阳",
            "PINA EDITION 第十四次的秋天",
            "虹之桥",
            "16.8.5",
            "伤害的界限突破",
            "Objectors! ~VRMMO开发秘话~",
            "魔法科高校的劣等生×SAO联合企划 刀剑神域篇",
            "画集短篇 Chromatic Colors",
            "画集短篇 Prismatic Colors",
            "电击文库25周年超感谢祭 夏天的结束与草帽",
            "电击文库2015周年超感谢祭 防御力 攻击力",
            "电击文库超感谢Fair2021 Blueish Memory",
            "电击文库超感谢Fair2022 再访第七层"
        ],
        [
            "剧场版特典小说",
            "《序列之争》观影特典 希望之歌",
            "《序列之争》BD特典 Cordial Chord",
            "Progressive 来场特典 开服次日",
            "Progressive BD特典 Memorable Song"
        ],
        [
            "Progressive 8 赤色焦热的狂想曲 下",
            "第十四章",
            "第十五章",
            "第十六章",
            "第十七章",
            "第十八章",
            "第十九章",
            "第二十章",
            "第二十一章",
            "第二十二章",
            "第二十三章",
            "第二十四章",
            "第二十五章",
            "第二十六章",
            "后记",
            "插图"
        ],
        [
            "第二十七卷 Unital Ring VI",
            "第一章",
            "第二章",
            "第三章",
            "第四章",
            "第五章",
            "第六章",
            "第七章",
            "第八章",
            "第九章",
            "第十章",
            "第十一章",
            "第十二章",
            "第十三章",
            "第十四章",
            "第十五章",
            "后记",
            "插图"
        ],
        [
            "第二十八卷 Unital Ring VII",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "后记",
            "插图"
        ]
    ]
    a = DownloadTask(numname='-2')
    a.rname = 'D:/HuaweiMoveData/Users/he660/Desktop/test'
    a.name = '刀剑神域(SAO／ALO／GGO／UW)'
    a.allname = allname
    a.txt_split()


if __name__ == '__main__':
    pass
