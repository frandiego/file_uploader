from joblib import Parallel, delayed
from functools import partial
from pathlib import Path
from PIL import Image
import os
import re

class Structure:

    @staticmethod
    def mkdir(path: str) -> None:
        os.system(f'mkdir -p {os.path.realpath(os.path.expanduser(path))}')

    @classmethod
    def parallel(cls, function, iterator: map, cores: int) -> map:
        return Parallel(n_jobs=cores)(delayed(function)(i) for i in iterator)

    
    @classmethod
    def list_files(
            cls, 
            path: str, 
            extensions:str=None, 
            ) -> list:
        """ List Files Recursively within a path filtered by extensions

        Args:
            path (str): Path to find files
            extensions (str, optional): list of extensions like jpg, raf. Defaults to None.

        Returns:
            list: a generator of all files
        """
        ls = Path(path).rglob('*')
        if extensions:
            regex = re.compile('|'.join([rf'\.{i}$' for i in extensions]))
            ls = filter(lambda i: bool(regex.search(str(i.name).lower())), ls)
        return ls
    
    @staticmethod
    def key_time(
            path: Path, 
            pattern : str = re.compile, 
        ) -> tuple:
        """ Create the filename with time on it from the key 
        Args:
            path (Path): Filepath of the file
            pattern (str, optional): regex pattern of the new filename. Defaults to re.compile.

        Returns:
            tuple: (key of the picture, new filename of the picture)
        """
        filename = str(Path(path).name).split('.')[0]
        if len(filename) == 28:
            match = pattern.match(filename)
            if match:
                if match.string == filename:
                    key = filename.split('_')[-1]
                    return (key, filename)
        time = Image.open(str(path)).getexif().get(306)
        time = str(time).replace(' ', '-').replace(':','-')
        key = filename.split('_')[-1]
        return (key, time + '_' + key)
        
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
        filename = str(file.name).split('_')[-1]
        new_filename = str(regex.sub(lambda match: translit[match.group(0)], filename))
        year, year_month = new_filename[:4], new_filename[:7]
        return (file, os.path.join(str(path), year, year_month, new_filename))
    
    @staticmethod
    def move(tuple) -> None:
        filefrom, fileto = tuple
        if str(filefrom) != str(fileto):
            filefrom.rename(str(fileto))
    
    @classmethod
    def make(
            cls, 
            path, 
            extensions: list, 
            raw_extensions: list, 
            cores: int, 
        ) -> None:
        """_summary_

        Args:
            path (_type_): main path of the pictures
            extensions (list): name of pictures extenstions like jpg
            raw_extensions (list): name of raw pictures extensions like raf
            cores (int): number of cores to parallelize process
        """
        pictures = cls.list_files(path=path, extensions=extensions)
        pattern = re.compile(r"^([0-9]+(-[0-9]+)+)_[a-z0-9]+$", re.IGNORECASE)
        fun = partial(cls.key_time, pattern = pattern)
        translit = dict(cls.parallel(function=fun, iterator=pictures, cores=cores))
        all_files = cls.list_files(path=path, extensions=extensions + raw_extensions)
        regex = re.compile('|'.join(map(re.escape, translit)))
        fun = partial(cls.travel, regex=regex, translit=translit, path=path)
        travel_dict = dict(cls.parallel(function=fun, iterator=all_files, cores=cores))
        folders = set(map(lambda i: Path(i).parent._str, travel_dict.values()))
        for folder in list(folders):
            cls.mkdir(folder)
        cls.parallel(function=cls.move, iterator=travel_dict.items(), cores=cores)
        