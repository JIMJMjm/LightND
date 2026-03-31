from time import sleep
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, overload

from urllib.parse import quote
import requests as rq
from bs4 import BeautifulSoup as bs
import urllib3

from config import CONFIG
from book_struct import HmzedBook

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/138.0.0.0 Safari/537.36'}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_WAORKERS = CONFIG["MAX_THREAD_WORKER"]
IRST = CONFIG["ILLUSTRATION_REQUEST_SLEEP_TIME"]
TRST = CONFIG["TEXT_REQUEST_SLEEP_TIME"]


def decode_add(address: str):
    encoded = quote(address, safe='/:')
    return encoded


class GetRq:
    def __init__(self, _url: str):
        self.url = _url

        self.response: rq.Response | None = None
        self.soup = None
        self.numname = ''
        self.copyright = False

    def request(self, gbk=False) -> None:
        self.response = rq.get(url=self.url, headers=HEADER)
        if gbk:
            self.response.encoding = 'GBK'

    def book_page_parser(self):
        """
        To get NovelName, Author, Bunko, Genre, Description and NumName from book/*.htm page
        :return: None
        """
        self.soup = bs(self.response.text, 'html.parser')
        bs_content = self.soup.find('div', id='content')
        bs_all_b = bs_content.find_all('b')
        str_all_b = [i.text for i in bs_all_b]
        Genre: list[str] = []
        for i in str_all_b[1:]:
            if '作品Tags：' in i:
                Genre = i[7:].split(' ')
            if 'JAR电子书下载' in i:
                self.copyright = True

        str_head = self.soup.find('title').text.split(' - ')
        NovelName, Author, Bunko = str_head[:3]

        bs_des = bs_content.find_all('span', style='font-size:14px;')
        Description = bs_des[-1].text.replace('\r', '')

        self.numname = self.url.strip('/').split('/')[-1].split('.')[0]

        return NovelName, Author, Description, Genre, Bunko, self.copyright

    def index_page_parser(self):
        """
        To get Numname, AllNet and Allname from */index.htm
        :return: None
        """
        self.soup = bs(self.response.text, 'html.parser')
        dd = self.soup.find_all('td')
        allnet: list[list[str]] = []
        allname: list[list[str]] = []
        book = []
        titles = []
        for i in dd:
            i_class = i.get('class')
            i_text = i.text
            if i_class == ['vcss']:
                if not book:
                    book.append(i_text)
                    titles.append(i_text)
                    continue
                allnet.append(book)
                allname.append(titles)
                book = [i_text]
                titles = [i_text]
            if i_class == ['ccss'] and i_text != '\xa0':
                ia = i.find('a')
                book.append(ia.get('href'))
                titles.append(ia.text)
        if len(book) > 1:
            allnet.append(book)
            allname.append(titles)
        self.numname = self.url.strip('/').split('/')[-2]

        return allnet, allname

    def thumbrail_page_parser(self) -> bytes:
        """
        Check if thumbrail exists. If it does, return instantly; else, download the thumbrail.
        No need for address input.
        :return: bytes
        """
        self.numname = self.url.strip('/').split('/')[-2]
        return self.image_page_parser()

    def image_folder_page_parser(self) -> list[bytes]:
        self.soup = bs(self.response.text, 'html.parser')
        bs_allimg = self.soup.find_all('div', class_='divimage')
        img_net_list: list[str] = [i.find('a').get('href') for i in bs_allimg]
        with ThreadPoolExecutor(max_workers=MAX_WAORKERS) as executor:
            futures = []
            for i in img_net_list:
                future = executor.submit(GetRq(i).run)
                futures.append(future)
            for future in futures:
                future.result()
        return [i.result() for i in futures]

    def image_page_parser(self) -> bytes:
        return self.response.content

    def text_page_parser(self):
        self.soup = bs(self.response.text, 'html.parser')
        title = self.soup.find('div', id='title').text
        con_text = self.soup.find('div', id='content').get_text()
        con_text = con_text.strip()[38:-50].replace('\r\n\xa0\xa0\xa0\xa0', '')
        return f'{title}\n{con_text}'

    def book_node_parser(self) -> str:
        self.soup = bs(self.response.text, 'html.parser')
        return self.soup.text.replace('\r', '').replace('\n\n', '\n')

    def test_parser(self):
        self.soup = bs(self.response.text, 'html.parser')
        return self.soup.text

    @overload
    def run(self, _type: Literal['p']) -> bytes:
        ...

    @overload
    def run(self, _type: Literal['i']) -> tuple[list[list[str]], list[list[str]]]:
        ...

    @overload
    def run(self, _type: Literal['b']) -> tuple[str, str, str, list[str], str, bool]:
        ...

    @overload
    def run(self, _type: Literal['f']) -> list[bytes]:
        ...

    @overload
    def run(self, _type: Literal['t']) -> str:
        ...

    @overload
    def run(self, _type: Literal['m']) -> bytes:
        ...

    @overload
    def run(self, _type: Literal['w']) -> str:
        ...

    @overload
    def run(self, _type: Literal['o']) -> None:
        ...

    @overload
    def run(self, _type: Literal['test']) -> bs:
        ...

    def run(self, _type: Literal['i', 'b', 'f', 't', 'p', 'm', 'w', 'o', 'test'] = 'p'):
        """
        Run the GetRq object, return the data as the type requests.
        """
        self.request(True)
        if _type == 'i':
            sleep(TRST)
            return self.index_page_parser()
        if _type == 'b':
            sleep(TRST)
            return self.book_page_parser()
        if _type == 'f':
            sleep(TRST)
            return self.image_folder_page_parser()
        if _type == 't':
            sleep(TRST)
            return self.text_page_parser()
        if _type == 'p':
            sleep(IRST)
            return self.image_page_parser()
        if _type == 'm':
            sleep(TRST)
            return self.thumbrail_page_parser()
        if _type == 'w':
            sleep(TRST)
            return self.book_node_parser()
        if _type == 'o':
            sleep(TRST)
            return self.soup
        if _type == 'test':
            sleep(TRST)
            return self.test_parser()


def get_alllist(numname: str, typ: str = 'allnet'):
    alllist = GetRq(f'https://www.wenku8.cc/novel/{int(numname) // 1000}/{numname}/index.htm').run(_type='i')
    if typ == 'allnet':
        return alllist[0]
    elif typ == 'allname':
        return alllist[1]
    else:
        return alllist


@overload
def get_fullinfo(numname: str, return_type: Literal[0]) -> dict: ...


@overload
def get_fullinfo(numname: str, return_type: Literal[1]) -> HmzedBook: ...


def get_fullinfo(numname: str, return_type: Literal[0, 1]):
    """

    :param numname:
    :param return_type: 1 for hmzBook, 0 for dict.
    :return:
    """
    modl = numname[0] if len(numname) > 3 else '0'
    allnet, allname = GetRq(f'https://www.wenku8.cc/novel/{modl}/{numname}/index.htm').run('i')
    name, writer, descrp, genre, bunko, cy = GetRq(f'https://www.wenku8.cc/book/{numname}.htm').run('b')

    if not return_type:
        return {'numname': numname, 'name': name, 'writer': writer,
                'allnet': allnet, 'allname': allname, 'description': descrp,
                'genre': genre, 'bunko': bunko, 'copyright': cy, }

    return HmzedBook(numname=numname, name=name, writer=writer,
                     allnet=allnet, allname=allname, description=descrp)
