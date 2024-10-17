from structure import Structure
from functools import partial
from pcloud import PyCloud
from loguru import logger
from src import SRC
import os


class PCloud:
    folder: str = None
    list_files: list = None

    def __init__(
            self, 
            username: str, 
            password: str, 
            ) -> None:
        self.client = PyCloud(
            username=username,
            password=password, 
            endpoint='eapi', 
        )

    def _set_folder(self, folder: str) -> None:
        self.folder = '/' + '/'.join(folder.split('/'))

    def _list_files(self, path: str, extensions: list) -> None:
        if not self.list_files:
            ls = Structure.list_pictures(path=path, extensions=extensions)
            self.list_files = sorted(set(ls))
        return self.list_files
    
    def create_folder_if_not_exists(
            self, 
            path: str, 
        ) -> None:
        """ Create a Folder and its parents if does not exists in Pcloud

        Args:
            path (str): full path of the folder to create
        """
        folders = list(filter(lambda i: i!='', path.split('/')))
        for i in range(len(folders)):
            path = '/' + os.path.join(*folders[:i+1])
            logger.info(f"Checking if {path} exists in PCloud")
            self.client.createfolderifnotexists(path=path)

    def check_folders(
            self, 
            pcloudpath: str, 
            path: str, 
            extensions: list, 
        ) -> None:
        """ Check if the folders in Pcloud

        Args:
            pcloudpath (str): Main Path of pictures in Pcloud
            path (str): path for pictures structured
            extensions (list): extensions of pictures to upload
        """
        ls =  self._list_files(path=path, extensions=extensions)
        folders =  set(map(lambda i: i.parent._str, ls))
        pcloud_folders = [i.replace(path, pcloudpath) for i in folders]
        for folder in pcloud_folders:
            self.create_folder_if_not_exists(path=folder)


    def upload_files(
            self, 
            files: list, 
            path: str,  
            pcloudpath:str, 
    ) -> None:
        """upload a list of files to pcloud

        Args:
            files (list): list of files
            path (str): path where local files
            pcloudpath (str): folder of pcloud pictures
        """
        ls = list(map(lambda i: (os.path.dirname(str(i)), i), files))
        folders = sorted(set(map(lambda i: i[0], ls)))
        
        move_dict = dict(zip(folders, list(list(
            map(lambda i: str(i[1]), 
                filter(lambda i: i[0]==f, ls))) 
            for f in folders)))
        
        for local_path, files in move_dict.items():
            pcloud_path = str(local_path).replace(path, pcloudpath)
            logger.info(f"Uploading {len(files)} to {pcloud_path}")
            self.client.uploadfile(files=files, path=str(pcloud_path))

    
    def upload(
            self, 
            path: str, 
            extensions: list, 
            cores: int, 
    ) -> None:
        """upload all files to pcloud

        Args:
            path (str): local path of files
            extensions (list): extensions os files
            cores (int): cores to paralelize
        """
        files = self._list_files(path=path, extensions=extensions)
        logger.info(f"Uploading {len(files)} to PCloud {self.folder}")
        fun = partial(self.upload_files, path=path, pcloudpath=self.folder)
        SRC.parallel(
            function=fun, 
            values=SRC.chunks(values=files, n=cores), 
            cores=cores,
        )
