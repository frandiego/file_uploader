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
    temporary_path: str = None

    def __init__(
        self,
        path: str, 
        copy: bool, 
    ) -> None:
        self.path = os.path.realpath(os.path.expanduser(path))
        self.copy = bool(copy)

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
        key = filename.split("_")[-1]
        if len(filename) == 28:
            match = pattern.match(filename)
            if match:
                if match.string == filename:
                    return (key, filename)
        else:
            try:
                time = Image.open(str(path)).getexif().get(306)
                time = str(time).replace(" ", "-").replace(":", "-")
                return (key, time + "_" + key)
            except Exception:
                return (key, None)
        return None

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
    def move_file(tuple) -> None:
        filefrom, fileto = tuple
        if str(filefrom) != str(fileto):
            Path(filefrom).rename(str(fileto))

    @staticmethod
    def copy_file(tuple) -> None:
        filefrom, fileto = tuple
        if str(filefrom) != str(fileto):
            os.system(f"cp {filefrom} {fileto}")


    def make(self) -> None:
        """Sort and Make a Structure for the pictures

        Args:
            path (_type_): main path of the pictures
            cores (int): number of cores to parallelize process
        """
        logger.info(f"Sorting all pictures in {self.path}")
        fun = partial(self.key_time, pattern=self.file_pattern)
        translit = dict(filter(bool,SRC.parallel(function=fun, values=SRC.list_files(self.path), cores=self.cores)))
        regex = re.compile("|".join(map(re.escape, translit)))
        path = self.path if not self.temporary_path else self.temporary_path
        fun = partial(self.travel, regex=regex, translit=translit, path=path)
        travel_dict = dict(SRC.parallel(function=fun, values=SRC.list_files(path), cores=self.cores))
        folders = set(map(lambda i: Path(i).parent._str, travel_dict.values()))
        for folder in list(folders):
            SRC.mkdir(folder)
        fun = self.copy_file if self.copy else self.move_file
        SRC.parallel(function=fun, values=travel_dict.items(), cores=self.cores)