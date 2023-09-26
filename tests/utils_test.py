import os
import shutil
import yaml
import shortuuid


TEST_OBJECT_PREFIX = "test_exim"

def mk_test_object_name_default():
    return f"{TEST_OBJECT_PREFIX}_{mk_uuid()}"

def mk_uuid():
    return shortuuid.uuid()


def create_output_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)


def compare_dirs(d1, d2):
    from filecmp import dircmp
    def _compare_dirs(dcmp):
        if len(dcmp.diff_files) > 0 or len(dcmp.left_only) > 0 or len(dcmp.right_only) > 0:
            if len(dcmp.diff_files) == 1:
                if dcmp.diff_files[0] == "MLmodel": # run_id differs because we changed it to the imported run_id
                    return True
            return False
        for sub_dcmp in dcmp.subdirs.values():
            if not _compare_dirs(sub_dcmp):
                return False
        return True
    return _compare_dirs(dircmp(d1, d2))


def create_run_artifact_dirs(output_dir):
    dir1 = create_run_artifact_dir(output_dir, "run1")
    dir2 = create_run_artifact_dir(output_dir, "run2")
    return dir1, dir2


def create_run_artifact_dir(output_dir, run_name):
    dir = os.path.join(output_dir, "artifacts", run_name)
    create_output_dir(dir)
    return dir


def read_config_file(path="config.yaml"):
    with open(path,  encoding="utf-8") as f:
        dct = yaml.safe_load(f)
        print(f"Config for '{path}':")
        for k,v in dct.items():
            print(f"  {k}: {v}")
    return dct
