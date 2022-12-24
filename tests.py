import os

engine_path: str


def test_find_ia_path(target: str, path='', n= 0) -> str:
    """
    find recursively the path of the IA engine
    return path when found else nothing
    """
    global engine_path

    if path == '':
        path = os.getcwd()
    print("Le répertoire courant est : " + path, "n =",  n)
    list_files_only = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    list_dir_only = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    for f in list_files_only:
        if f == target:
            engine_path = path + "/" + f

    for d in list_dir_only:
        _path = path + "/" + d
        print(_path)
        test_find_ia_path(target, path=_path, n=n+1)
        _path = ''


if __name__ == "__main__":
    test_find_ia_path("stockfish")
    print(engine_path)