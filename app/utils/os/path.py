import os

def mkdir_ignore_exists(f_path: str | os.PathLike[str]):
    if not os.path.exists(f_path):
        os.mkdir(f_path)
