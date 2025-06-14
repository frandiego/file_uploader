from typing import List, Any, Optional, Callable, Iterator
from joblib import Parallel, delayed
from types import SimpleNamespace
from loguru import logger
from pathlib import Path
import questionary
import os


class SRC:
    """Utility class for file operations and CLI interactions.

    This class provides static methods for common file operations, parallel processing,
    and command line interface functionality.
    """

    @staticmethod
    def is_not_hidden(path: str) -> bool:
        """Check if a path does not contain hidden directories/files.

        Args:
            path: File system path to check.

        Returns:
            bool: True if path contains no hidden components, False otherwise.
        """
        return not any(map(lambda i: i.startswith("."), str(path).split("/")))

    @classmethod
    def list_files(cls, path: str) -> filter:
        """List all non-hidden files recursively in a directory.

        Args:
            path: Directory path to search.

        Returns:
            filter: Iterator of non-hidden file paths.
        """
        return filter(cls.is_not_hidden, Path(path).rglob("*"))

    @staticmethod
    def chunks(values: list, n: int) -> Iterator[list]:
        """Split a list into chunks of specified size.

        Args:
            values: List to split into chunks.
            n: Size of each chunk.

        Yields:
            List containing n elements from values.
        """
        for i in range(0, len(values), n):
            yield values[i : i + n]

    @staticmethod
    def mkdir(path: str) -> None:
        """Create directory and all parent directories if they don't exist.

        Args:
            path: Directory path to create.
        """
        os.system(f"mkdir -p {os.path.realpath(os.path.expanduser(path))}")

    @classmethod
    def parallel(cls, function: Callable, values: map, cores: int) -> List[Any]:
        """Execute a function in parallel across multiple cores.

        Args:
            function: Function to execute in parallel.
            values: Iterator of values to process.
            cores: Number of CPU cores to use.

        Returns:
            List of results from parallel execution.
        """
        return Parallel(n_jobs=cores, backend='threading')(delayed(function)(i) for i in values)

    @staticmethod
    def make_questions(entity: Any, questions: questionary.Form) -> Optional[Any]:
        """Create and process questionary form for user input.

        Args:
            entity: Class or function to instantiate with answers.
            questions: Questionary form containing questions.

        Returns:
            Instance of entity initialized with answers, or None if validation fails.
        """
        answers = questions.ask()
        if not any(filter(bool, answers.values())):
            logger.error(f"Parameters {', '.join(answers)} need to be answered")
            return None
        try:
            return entity(**answers)
        except Exception as e:
            logger.error(e)
            return None

    @classmethod
    def cli(cls) -> SimpleNamespace:
        """Run command line interface for file operations.

        Creates interactive prompts for configuring file structure organization
        and PCloud upload settings.

        Returns:
            SimpleNamespace containing configured Structure and PCloud instances.
        """
        from pycloud import PCloud
        from structure import Structure

        structure = None
        pcloud = None

        if questionary.confirm("Want To Sort the pictures").ask():
            questionary.print("Setting Pictures Files", style="bold italic fg:yellow")
            structure = cls.make_questions(
                Structure,
                questionary.form(
                    path=questionary.path(
                        message="Where are the pictures?",
                    ),
                    copy=questionary.confirm(
                        message="Copy files",
                        default=False,
                    ),
                ),
            )

            if questionary.confirm("Use a Temporary Folder").ask():
                temp_path = questionary.path(
                    message="Where is the Temporary Folder"
                ).ask()
                structure.temporary_path = os.path.expanduser(temp_path)

        if questionary.confirm("Want To upload the files to PCloud").ask():
            questionary.print("Setting PCloud client", style="bold italic fg:yellow")
            pcloud = cls.make_questions(
                PCloud,
                questionary.form(
                    username=questionary.text(
                        message="PCloud Username",
                    ),
                    password=questionary.password(
                        message="PCloud Password",
                    ),
                ),
            )

            folders = (
                pcloud.client.listfolder(folderid=0)
                .get("metadata", {})
                .get("contents", [])
            )

            folder_names = [i.get("name") for i in folders]
            pcloud_folder = questionary.select("Pcloud Folder", folder_names).ask()
            path = questionary.path(message="Where are the pictures in local?").ask()

            pcloud._set_folder(folder=pcloud_folder)
            pcloud._set_path(path=path)

        return SimpleNamespace(**{"structure": structure, "pcloud": pcloud})
