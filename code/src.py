from joblib import Parallel, delayed
from types import SimpleNamespace
from typing import Tuple, Text
from loguru import logger
from pathlib import Path
import questionary
import os


class SRC:

    @staticmethod
    def is_not_hidden(path: str) -> bool:
        return not any(map(lambda i: i.startswith("."), str(path).split("/")))

    @classmethod
    def list_files(cls, path: str) -> filter:
        return filter(cls.is_not_hidden, Path(path).rglob("*"))

    @staticmethod
    def chunks(values: list, n: int):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(values), n):
            yield values[i : i + n]

    @staticmethod
    def mkdir(path: str) -> None:
        os.system(f"mkdir -p {os.path.realpath(os.path.expanduser(path))}")

    @classmethod
    def parallel(cls, function, values: map, cores: int) -> map:
        return Parallel(n_jobs=cores)(delayed(function)(i) for i in values)

    @staticmethod
    def make_questions(entity, questions):
        answers = questions.ask()
        if not any(filter(bool, answers.values())):
            logger.error(f"Parameters {', '.join(answers)} need to be answered")
        else:
            try:
                res = entity(**answers)
                return res
            except Exception as e:
                logger.error(e)

    @classmethod
    def cli(cls) -> Tuple[Text, Text, Text]:
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

            use_temp_folder = questionary.confirm("Use a Temporary Folder").ask()
            if use_temp_folder:
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
