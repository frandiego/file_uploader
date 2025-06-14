from functools import partial
from joblib import cpu_count
from loguru import logger
from pathlib import Path
from PIL import Image
import os
import re

from src import SRC


class Structure:
    """Class for organizing and structuring image files.

    This class provides functionality to sort and organize image files based on their
    timestamps and filenames. It can either move or copy files into a structured directory
    hierarchy.

    Attributes:
        file_pattern: Regex pattern for matching filenames with timestamps.
        cores: Number of CPU cores to use for parallel processing.
        temporary_path: Optional temporary path for file operations.
    """

    file_pattern = re.compile(r"^([0-9]+(-[0-9]+)+)_[a-z0-9]+$", re.IGNORECASE)
    cores: int = int(cpu_count())
    temporary_path: str = None

    def __init__(self, path: str, copy: bool) -> None:
        """Initialize Structure instance.

        Args:
            path: Base directory path containing images to organize.
            copy: If True, copy files instead of moving them.
        """
        self.path = os.path.realpath(os.path.expanduser(path))
        self.copy = bool(copy)

    @staticmethod
    def key_time(path: Path, pattern: re.Pattern) -> tuple:
        """Extract key and timestamp from image filename.

        Attempts to get timestamp either from filename pattern or image EXIF data.

        Args:
            path: Path to the image file.
            pattern: Regex pattern for matching timestamp in filename.

        Returns:
            Tuple of (key, timestamp_filename) or None if no timestamp found.
            key is the unique identifier from filename.
            timestamp_filename is the new filename with timestamp.
        """
        filename = str(Path(path).name).split(".")[0]
        key = filename.split("_")[-1]

        if len(filename) == 28:
            match = pattern.match(filename)
            if match and match.string == filename:
                return (key, filename)

        try:
            time = Image.open(str(path)).getexif().get(306)
            time = str(time).replace(" ", "-").replace(":", "-")
            return (key, time + "_" + key)
        except Exception:
            return (key, None)

        return None

    @staticmethod
    def travel(file: str, path: str, regex: re.Pattern, translit: dict) -> tuple:
        """Generate source and destination paths for file reorganization.

        Args:
            file: Source file path.
            path: Base destination directory path.
            regex: Regex pattern for matching keys in translit dictionary.
            translit: Dictionary mapping keys to timestamp-based filenames.

        Returns:
            Tuple of (source_path, destination_path).
        """
        filename = str(file.name).split("_")[-1]
        new_filename = str(regex.sub(lambda match: translit[match.group(0)], filename))
        year, year_month = new_filename[:4], new_filename[:7]
        return (file, os.path.join(str(path), year, year_month, new_filename))

    @staticmethod
    def move_file(paths: tuple) -> None:
        """Move a file from source to destination path.

        Args:
            paths: Tuple of (source_path, destination_path).
        """
        filefrom, fileto = paths
        if str(filefrom) != str(fileto):
            Path(filefrom).rename(str(fileto))

    @staticmethod
    def copy_file(paths: tuple) -> None:
        """Copy a file from source to destination path.

        Args:
            paths: Tuple of (source_path, destination_path).
        """
        filefrom, fileto = paths
        if str(filefrom) != str(fileto):
            os.system(f"cp {filefrom} {fileto}")

    def travel_dict(self) -> dict:
        """Creates a mapping of source files to their destination paths.

        This method processes all pictures in the configured path, extracting timestamps
        from EXIF data to generate new filenames. It then creates a mapping between
        source files and their reorganized destination paths.

        Returns:
            A dictionary mapping source file paths to destination file paths.

        Note:
            The destination paths will use either self.path or self.temporary_path
            as the base directory, depending on configuration.
        """
        logger.info(f"Sorting all pictures in {self.path}")

        # Generate timestamp translations
        fun = partial(self.key_time, pattern=self.file_pattern)
        translit = dict(
            filter(
                bool,
                SRC.parallel(
                    function=fun, 
                    values=SRC.list_files(self.path), 
                    cores=self.cores,
                ),
            )
        )

        logger.info('translit')
        #logger.info(translit)

        # Generate destination paths
        regex = re.compile("|".join(map(re.escape, translit)))
        fun = partial(self.travel, regex=regex, translit=translit, path=self.path)
        values = list(SRC.list_files(self.path))
        travel_dict =  dict(
            SRC.parallel(
                function=fun, 
                values=values,
                cores=self.cores,
            )
        )

        if self.temporary_path:
            path = self.path.rstrip('/')
            temp_path = self.temporary_path.rstrip('/')
            for k, v in travel_dict.items():
                travel_dict[k] = str(v).replace(path, temp_path)
        return travel_dict

    def make(self) -> None:
        """Create directory structure and move or copy files.

        This method creates the necessary directory structure and then moves or copies
        files to their new locations based on the travel_dict.
        """
        travel_dict = self.travel_dict()

        logger.info('travel_dict')
        logger.info(travel_dict)

        # Create directory structure
        folders = set(map(lambda i: Path(i).parent._str, travel_dict.values()))
        for folder in list(folders):
            SRC.mkdir(folder)

        # Move or copy files
        fun = self.copy_file if self.copy else self.move_file
        SRC.parallel(function=fun, values=travel_dict.items(), cores=self.cores)
