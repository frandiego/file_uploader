from functools import partial
from joblib import cpu_count
from loguru import logger
from pathlib import Path
from PIL import Image
import os
import re
from src import SRC


class Structure:
    file_pattern = re.compile(r"^([0-9]+(-[0-9]+)+)_[a-z0-9]+$", re.IGNORECASE)
    cores: int = int(cpu_count())

    def __init__(
        self,
        path: str,
        extensions: str,
        raw_extensions: str,
    ) -> None:
        self.path = os.path.realpath(os.path.expanduser(path))
        self.extensions = list(map(lambda i: i.lower(), extensions.split(",")))
        self.raw_extensions = list(map(lambda i: i.lower(), raw_extensions.split(",")))

    @staticmethod
    def list_pictures(path: str, extensions: list) -> list:
        ls = Path(os.path.realpath(os.path.expanduser(path))).rglob("*")
        if extensions:
            regex = re.compile("|".join([rf"\.{i}$" for i in extensions]))
            ls = filter(lambda i: bool(regex.search(str(i.name).lower())), ls)
        return ls

    @staticmethod
    def key_time(
        path: Path,
        pattern: str = re.compile,
    ) -> tuple:
        """Create the filename with time on it from the key
        Args:
            path (Path): Filepath of the file
            pattern (str, optional): regex pattern of the new filename. Defaults to re.compile.

        Returns:
            tuple: (key of the picture, new filename of the picture)
        """
        filename = str(Path(path).name).split(".")[0]
        if len(filename) == 28:
            match = pattern.match(filename)
            if match:
                if match.string == filename:
                    key = filename.split("_")[-1]
                    return (key, filename)
        time = Image.open(str(path)).getexif().get(306)
        time = str(time).replace(" ", "-").replace(":", "-")
        key = filename.split("_")[-1]
        return (key, time + "_" + key)

    @staticmethod
    def travel(
        file: str,
        path: str,
        regex: re.compile,
        translit: dict,
    ) -> tuple:
        """Information of the to rename the files (from -> to)

        Args:
            file (str): name of the files
            path (str): path of the main folder
            regex (re.compile): regex to index from translit dict
            translit (dict): dictionary to translate keys to time keys

        Returns:
            tuple: (filepath, new filepath)
        """
        filename = str(file.name).split("_")[-1]
        new_filename = str(regex.sub(lambda match: translit[match.group(0)], filename))
        year, year_month = new_filename[:4], new_filename[:7]
        return (file, os.path.join(str(path), year, year_month, new_filename))

    @staticmethod
    def move(tuple) -> None:
        filefrom, fileto = tuple
        if str(filefrom) != str(fileto):
            filefrom.rename(str(fileto))

    def make(self) -> None:
        """Sort and Make a Structure for the pictures

        Args:
            path (_type_): main path of the pictures
            extensions (list): name of pictures extenstions like jpg
            raw_extensions (list): name of raw pictures extensions like raf
            cores (int): number of cores to parallelize process
        """
        logger.info(f"Sorting all pictures in {self.path}")
        fun = partial(self.key_time, pattern=self.file_pattern)
        pictures = self.list_pictures(path=self.path, extensions=self.extensions)
        translit = dict(SRC.parallel(function=fun, values=pictures, cores=self.cores))
        regex = re.compile("|".join(map(re.escape, translit)))
        fun = partial(self.travel, regex=regex, translit=translit, path=self.path)
        self.extensions += self.raw_extensions
        all_files = self.list_pictures(
            path=self.path, extensions=self.extensions + self.raw_extensions
        )
        travel_dict = dict(
            SRC.parallel(function=fun, values=all_files, cores=self.cores)
        )
        folders = set(map(lambda i: Path(i).parent._str, travel_dict.values()))
        for folder in list(folders):
            SRC.mkdir(folder)
        SRC.parallel(function=self.move, values=travel_dict.items(), cores=self.cores)
