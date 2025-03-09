import logging
import shutil

def copy_file_to(path_src, path_dest):
    logger = logging.getLogger("src.util.others")

    try:
        path_parent_dest_dir = path_dest.parent
        path_parent_dest_dir.mkdir(exist_ok = True)
        shutil.copy2(path_src, path_dest)
    except Exception as e:
        logger.exception(f"Exception during copy_file_to(path_src = {path_src}, path_dest = {path_dest})")

def copy_dir_to_recursively(path_dir_src, path_dir_dest):
    shutil.copytree(path_dir_src, path_dir_dest, dirs_exist_ok = True)

def delete_dir_recursively(path_dir):
    if (path_dir.exists()):
        shutil.rmtree(path_dir)

def create_dir(path_dir):
    path_dir.mkdir(parents = True, exist_ok = True)