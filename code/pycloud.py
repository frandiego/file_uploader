from functools import partial
from joblib import cpu_count
from pcloud import PyCloud
from loguru import logger
import os

from src import SRC


class PCloud:
    """Class to handle file uploads to PCloud storage service.

    Attributes:
        path (str): Local file system path to upload from.
        folder (str): Remote PCloud folder path to upload to.
        cores (int): Number of CPU cores to use for parallel uploads.
    """

    path: str = None
    folder: str = None
    cores: int = int(cpu_count())

    def __init__(self, username: str, password: str) -> None:
        """Initialize PCloud client.

        Args:
            username: PCloud account username.
            password: PCloud account password.
        """
        self.client = PyCloud(
            username=username,
            password=password,
            endpoint="eapi",
        )

    def _set_folder(self, folder: str) -> None:
        """Set the remote PCloud folder path.

        Args:
            folder: Remote folder path to set.
        """
        self.folder = "/" + "/".join(folder.split("/"))

    def _set_path(self, path: str) -> None:
        """Set the local file system path.

        Args:
            path: Local path to set.
        """
        self.path = os.path.realpath(os.path.expanduser(str(path)))

    def create_folder_if_not_exists(self, path: str) -> None:
        """Create a folder and its parents in PCloud if they don't exist.

        Args:
            path: Full path of the folder to create.
        """
        folders = list(filter(lambda i: i != "", path.split("/")))
        for i in range(len(folders)):
            path = "/" + os.path.join(*folders[: i + 1])
            logger.info(f"Checking if {path} exists in PCloud")
            self.client.createfolderifnotexists(path=path)

    def check_folders(self, pcloudpath: str, path: str) -> None:
        """Check and create necessary folders in PCloud.

        Args:
            pcloudpath: Main path in PCloud where files will be uploaded.
            path: Local path containing the file structure.
        """
        ls = SRC.list_files(path=path)
        folders = set(map(lambda i: i.parent._str, ls))
        pcloud_folders = [i.replace(path, pcloudpath) for i in folders]
        for folder in pcloud_folders:
            self.create_folder_if_not_exists(path=folder)

    def upload_files(self, files: list, path: str, pcloudpath: str) -> None:
        """Upload a list of files to PCloud.

        Args:
            files: List of files to upload.
            path: Local path containing the files.
            pcloudpath: Remote PCloud path to upload to.
        """
        ls = list(map(lambda i: (os.path.dirname(str(i)), i), files))
        folders = sorted(set(map(lambda i: i[0], ls)))

        move_dict = dict(
            zip(
                folders,
                list(
                    list(map(lambda i: str(i[1]), filter(lambda i: i[0] == f, ls)))
                    for f in folders
                ),
            )
        )

        for local_path, files in move_dict.items():
            pcloud_path = str(local_path).replace(path, pcloudpath)
            logger.info(f"Uploading {len(files)} to {pcloud_path}")
            self.client.uploadfile(files=files, path=str(pcloud_path))

    def upload(self) -> None:
        """Upload all files to PCloud using parallel processing.

        Uses multiple CPU cores to parallelize the upload process for better performance.
        Files are uploaded maintaining the local directory structure.
        """
        files = SRC.list_files(path=self.path)
        logger.info(f"Uploading {len(files)} to PCloud {self.folder}")
        fun = partial(
            self.upload_files,
            path=self.path,
            pcloudpath=self.folder,
        )
        SRC.parallel(
            function=fun,
            values=SRC.chunks(values=files, n=self.cores),
            cores=self.cores,
        )
