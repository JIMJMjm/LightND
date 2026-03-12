from urllib.parse import quote

from netwk import GetRq

ec = quote('中文', encoding='gbk')

m = GetRq(f'https://www.wenku8.cc/modules/article/search.php?searchtype=articlename&searchkey={ec}').run('test')

if __name__ == '__main__':
    print(ec)
    print(m)