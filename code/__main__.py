from src import SRC

src = SRC.cli()
if src.structure:
    src.structure.make()
if src.pcloud:
    src.pcloud.upload()
