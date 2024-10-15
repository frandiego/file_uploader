from joblib import cpu_count
import questionary

from structure import Structure
from pycloud import PCloud


username = questionary.text("PCloud username").ask()
password = questionary.password("PCloud password").ask()
CLIENT = PCloud(username=username, password=password)
path = questionary.path("Where are the pictures").ask()
pcloudpath = questionary.text("PCloud Folder").ask()
extensions = questionary.text("Picture extensions").ask()
raw_extensions = questionary.text("Raw Picture extensions").ask()
cores = int(cpu_count())

Structure.make(
    path=path, 
    extensions=extensions, 
    raw_extensions=raw_extensions, 
    cores=cores,
)

CLIENT.upload(
    path=path, 
    pcloudpath=pcloudpath, 
    extensions=extensions + raw_extensions, 
    cores=cores,
)
