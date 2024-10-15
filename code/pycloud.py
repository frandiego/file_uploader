from pcloud import PyCloud
from pathlib import Path
from structure import Structure
import os

class Transfer:

    def __init__(
            self, 
            username: str, 
            password: str, 
            ) -> None:
        self.client = PyCloud(username=username, password=password, endpoint='eapi')

    def create_folder_if_not_exists(self, path: str) -> None:
        folders = list(filter(lambda i: i!='', path.split('/')))
        for i in range(len(folders)):
            path = '/' + os.path.join(*folders[:i+1])
            self.client.createfolderifnotexists(path=path)

    def check_folders(self, pcloudpath: str, path: str, extensions: list) -> None:
        ls = Structure.list_files(path=path, extensions=extensions)
        folders =  set(map(lambda i: i.parent._str, ls))
        folders = [i.replace(path, pcloudpath) for i in folders]
        print(folders)

