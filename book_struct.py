from dataclasses import dataclass, field

from typing_extensions import overload

from config import save_json, CONFIG, confirm_name


class Book:
    def __init__(self, *, numname: str, name: str, writer: str):
        self.name = confirm_name(name)
        self.numname = numname
        self.writer = writer

    def __str__(self):
        return f'{self.numname}-{self.writer}-{self.name}'

    def __repr__(self):
        return f'{self.numname}-{self.writer}-{self.name}'

    def __eq__(self, other):
        return self.numname == other.numname

    def hasSameName(self, other: 'Book'):
        return self.name == other.name

    def __contains__(self, item):
        return self.numname == item or self.name == item or self.writer == item

    def strictlyEqual(self, other: 'Book'):
        return self.numname == other.numname and self.writer == other.writer and self.name == other.name


@dataclass
class BookLuxury:
    prg: list = field(default_factory=list)
    rtg: dict = field(default_factory=dict)
    fav: int = 0
    lck: int = 0

    def toDict(self):
        return {
            'prg': self.prg,
            'rtg': self.rtg,
            'fav': self.fav,
            'lck': self.lck
        }


class BankedBook(Book):
    @overload
    def __init__(self, *, numname, name, writer,
                 bunko: str, genre: list[str], addtime: str, lux: dict, directory=''):...

    @overload
    def __init__(self, *, numname, name, writer,
                 bunko: str, genre: list[str], addtime: str, lux: BookLuxury, directory=''): ...

    def __init__(self, *, numname, name, writer,
                 bunko: str, genre: list[str], addtime: str, lux: BookLuxury | dict,
                 directory=''):
        """
        The book data to be stored in ``book.json``
        :param bunko:
        :param genre:
        :param addtime: The addtime of the book
        :param lux: Luxury data. Input as dict or BookLuxury.
        :param directory: The directory ``{{numname}}.hmz`` is at.
        """
        super().__init__(numname=numname, name=name, writer=writer)
        self.bunko = bunko
        self.genre = genre
        self.addtime = addtime
        if isinstance(lux, BookLuxury):
            self.lux = lux
        else:
            self.lux = BookLuxury(**lux)
        self.directory = directory

    def toDict(self):
        return {
            'numname': self.numname,
            'name': self.name,
            'writer': self.writer,
            'bunko': self.bunko,
            'genre': self.genre,
            'addtime': self.addtime,
            'lux': self.lux.toDict(),
            'directory': self.directory
        }

    # def __getitem__(self, item):
    #     pass


class HmzedBook(Book):
    def __init__(self, *, numname, name, writer,
                 allnet, allname, description=''):
        super().__init__(numname=numname, name=name, writer=writer)
        self.allnet = allnet
        self.allname = allname
        self.description = description

    def toDict(self):
        return {
            'numname': self.numname,
            'name': self.name,
            'writer': self.writer,
            'allnet': self.allnet,
            'allname': self.allname,
            'description': self.description,
        }

    def save_at(self, directory: str | None = None) -> None:
        if directory is None:
            directory = CONFIG['BANK_PATH']
        save_json(directory, self.toDict())


if __name__ == '__main__':
    a = Book(numname='11', writer='123', name='2211')
    bank = [Book(numname='11', writer='123', name='2211'), Book(numname='12', writer='321', name='2222')]
    bank[1].numname = '1'
    print(bank)
