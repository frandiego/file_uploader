from joblib import Parallel, delayed
from types import SimpleNamespace
from typing import Tuple, Text
from loguru import logger
import questionary
import os


class SRC:
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

        questionary.print("Setting Pictures Files", style="bold italic fg:yellow")

        structure = cls.make_questions(
            Structure,
            questionary.form(
                path=questionary.path(
                    message="Where are the pictures?",
                ),
                extensions=questionary.text(
                    message="What are the picture extensions?",
                ),
                raw_extensions=questionary.text(
                    message="What are the RAW picture extensions?",
                ),
            ),
        )

        use_temp_folder = questionary.confirm("Use a Temporary Folder").ask()
        if use_temp_folder:
            temp_path = questionary.path(message = "Wuere is the Temporary Folder").ask()
            structure.temporary_path = os.path.realpath(os.path.expanduser(temp_path))
            
        upload_files = questionary.confirm("Want To upload the files to PCloud").ask()
        if upload_files:
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
                pcloud.client.listfolder(folderid=0).get("metadata", {}).get("contents", [])
            )
            folder_names = [i.get("name") for i in folders]
            pcloud._set_folder(
                folder=questionary.select("Pcloud Folder", folder_names).ask()
            )
        else:
            pcloud = None


        return SimpleNamespace(**{"structure": structure, "pcloud": pcloud})
