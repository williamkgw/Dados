import shutil

def copy_file_to(path_src, path_dest):
    shutil.copy2(path_src, path_dest)

def copy_dir_to_recursively(path_dir_src, path_dir_dest):
    shutil.copytree(path_dir_src, path_dir_dest, dirs_exist_ok = True)

def delete_dir_recursively(path_dir):
    if (path_dir.exists()):
        shutil.rmtree(path_dir)

def create_dir(path_dir):
    path_dir.mkdir(parents = True, exist_ok = True)