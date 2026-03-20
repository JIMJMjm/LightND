from os import listdir as ldr
from typing import Literal

from requests import post, delete
from requests.auth import HTTPBasicAuth

from txtprocess import HFolder, ordered_ldr

BASE_URL = "https://read.lycnet.cn/api"
AUTH = HTTPBasicAuth('JIM_jmjm', 'Hmz20260202')


def upload_bookinfo(title, author, desc, cover_path) -> int:
    url = f"{BASE_URL}/admin/books/"
    data = {
        "title": title,
        "author": author,
        "description": desc
    }
    files = {
        "cover": open(cover_path, "rb")
    }
    response = post(url, data=data, files=files, auth=AUTH)
    return response.json().get('id')


def upload_chapter(book_id, title, content, vol):
    url = f"{BASE_URL}/admin/chapters/"
    data = {
        "book": book_id,
        "title": title,
        "content": content,
        "volume_name": vol
    }
    print(f'{title} opened.')
    response = post(url, data=data, auth=AUTH)
    print(f'{title} is{'n\'t' if not response.ok else ''} uploaded.')


def upload_illustration(book_id, vol, ill_path):
    url = f"{BASE_URL}/admin/illustrations/"
    data = {
        "book": book_id,
        "volume_name": vol
    }
    files = {
        "image": open(ill_path, "rb")
    }
    print(f'{ill_path} opened.')
    response = post(url, data=data, files=files, auth=AUTH)
    print(f'{ill_path} is{'n\'t' if not response.ok else ''} uploaded.')


def upload_volume(book_id, volume_path):
    volname = volume_path.split('/')[-1]
    vol_num = len(volname.split(' '))
    print(f'Uploading volume {volname}...')
    chapters = ordered_ldr(volume_path)
    illu_folder = [] if not chapters[1] else ordered_ldr(f'{volume_path}/插图', '.jpg')[0]
    text_folder = chapters[0]
    for i in text_folder:
        with open(f'{volume_path}/{i}', 'r', encoding='utf-8') as text:
            text_content = text.readlines()
        title = ' '.join(text_content.pop(0).strip().split(' ')[vol_num:])
        content = '\n'.join(text_content)
        upload_chapter(book_id, title, content, volname)

    for i in illu_folder:
        upload_illustration(book_id, volname, f'{volume_path}/插图/{i}')
    print(f'{volname} uploaded.')


def upload_Hfolder(Hfolder_path: str, cover_path: str = ''):
    Hfolder = HFolder(Hfolder_path, ignore_config=True)
    cover = cover_path if cover_path else Hfolder.cover
    bookid = upload_bookinfo(Hfolder.name, Hfolder.writer, Hfolder.discription, cover)

    for i in Hfolder:
        upload_volume(bookid, i)


def delete_resource(resource_type: Literal['books', 'chapters', 'illustrations'], resource_id):
    url = f"{BASE_URL}/admin/{resource_type}/{resource_id}/"
    response = delete(url, auth=AUTH)
    print(f"Delete Status: {response.status_code}")


if __name__ == '__main__':
    # upload_Hfolder('D:/ACGN/Novel/我们在「解读」上犯了错误(我们的『阅读理解』出错了)')
    for i in range(22, 25):
        delete_resource('books', i)
