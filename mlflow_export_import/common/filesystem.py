"""
Filesystem utilities - local or Databricks
"""

import os
import shutil


def mk_dbfs_path(path):
    return path.replace("/dbfs","dbfs:")


def mk_local_path(path):
    return path.replace("dbfs:","/dbfs")


def exists(path):
    os.path.exists(mk_local_path(path))


class DatabricksFileSystem():
    def __init__(self):
        import IPython
        self.dbutils = IPython.get_ipython().user_ns["dbutils"]

    def ls(self, path):
        return self.dbutils.fs.ls(mk_dbfs_path(path))

    def cp(self, src, dst, recursive=False):
        self.dbutils.fs.cp(mk_dbfs_path(src), mk_dbfs_path(dst), recursive)

    def rm(self, path, recurse=False):
        self.dbutils.fs.rm(mk_dbfs_path(path), recurse)

    def mkdirs(self, path):
        self.dbutils.fs.mkdirs(mk_dbfs_path(path))

    def write(self, path, content):
        self.dbutils.fs.put(mk_dbfs_path(path), content, True)


class LocalFileSystem():
    def __init__(self):
        pass

    def cp(self, src, dst, recurse=False):
        shutil.copytree(mk_local_path(src), mk_local_path(dst))

    def rm(self, path, recurse=False):
        shutil.rmtree(mk_local_path(path))

    def mkdirs(self, path):
        os.makedirs(mk_local_path(path),exist_ok=True)

    def write(self, path, content):
        with open(mk_local_path(path), "w", encoding="utf-8") as f:
            f.write(content)


def get_filesystem(dir):
    """ Return the filesystem object matching the directory path. """
    return DatabricksFileSystem() if dir.startswith("dbfs:") else LocalFileSystem()
