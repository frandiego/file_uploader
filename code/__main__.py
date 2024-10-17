from src import SRC

src = SRC.cli()
src.structure.make()
src.pcloud.upload(
    path=src.structure.path, 
    extensions=src.structure.extensions +  src.structure.raw_extensions, 
    cores=src.structure.cores, 
)
