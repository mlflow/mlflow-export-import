"""
Selects specified model from `export-models` directory and creates a new export directory with just that model and the experiment that its versions's runs belong to.
Assumes model version runs belong to one experiment and export just that experiment.
WIP.

"""

import os
import shutil
import click
from mlflow_export_import.common.click_options import opt_input_dir, opt_output_dir
from mlflow_export_import.common import io_utils
from mlflow_export_import.common.timestamp_utils import ts_now_fmt_local


def do_main(input_dir, output_dir, src_model_name, dst_model_name, dst_experiment_name):
    dst_model_name = dst_model_name or src_model_name
    do_manifest(input_dir, output_dir, src_model_name, dst_model_name, dst_experiment_name)
    src_experiment_name = do_models(input_dir, output_dir, src_model_name, dst_model_name, dst_experiment_name)
    do_experiments(src_experiment_name, dst_experiment_name, input_dir, output_dir)


def do_manifest(input_dir, output_dir, src_model_name, dst_model_name, dst_experiment_name):
    root = io_utils.read_file(mk_path(input_dir, "manifest.json"))
    info = root["info"]
    info["model_names"] = [ dst_model_name ]
    info["models"]["model_names"] = [ dst_model_name ]
    filter_dct = {
        "description":  "Filtered select model from all_model export directory. WIP.",
        "timestamp":  ts_now_fmt_local,
        "src_model_name": src_model_name,
        "dst_model_name": dst_model_name,
        "dst_experiment_name": dst_experiment_name,
        "input_dir": input_dir
    }
    root["info"] = { **{ "filter_info": filter_dct }, **info }
    io_utils.write_file(mk_path(output_dir, "manifest.json"), root)


def do_models(input_dir, output_dir, src_model_name, dst_model_name, dst_experiment_name):
    src_models_dir = os.path.join(input_dir, "models")
    src_root = io_utils.read_file(mk_path(src_models_dir,"models.json"))

    src_models = src_root["mlflow"]["models"]
    if not src_model_name in src_models:
        print(f"ERROR: Model '{src_model_name}' not found in: {src_models}")
        return

    dst_root = src_root.copy()
    dst_root["mlflow"]["models"] = [ dst_model_name ]

    # update the dst models.json
    dst_models_dir = mk_path(output_dir, "models")
    os.makedirs(dst_models_dir, exist_ok=True)
    models_path = mk_path(dst_models_dir, "models.json")
    io_utils.write_file(models_path, dst_root)

    # write the dst models dir
    src_path = mk_path(src_models_dir, src_model_name)
    dst_path = mk_path(dst_models_dir, dst_model_name)
    shutil.copytree(src_path, dst_path)

    return do_model(dst_model_name, dst_experiment_name, src_path, dst_path)


def do_model(dst_model_name, dst_experiment_name, src_dir, dst_dir):
    src_path = mk_path(src_dir, "model.json")
    src_root = io_utils.read_file(src_path)
    dst_root = src_root.copy()
    dst_model = dst_root["mlflow"]["registered_model"]
    dst_model["name"] = dst_model_name

    src_exp_name = do_versions(dst_model_name, dst_experiment_name, dst_model["versions"])

    dst_path = mk_path(dst_dir, "model.json")
    io_utils.write_file(dst_path, dst_root)

    return src_exp_name


def do_versions(dst_model_name, dst_experiment_name, dst_versions):
    src_exp_name = None
    for vr in dst_versions:
        vr["name"] = dst_model_name
        src_exp_name = vr["_experiment_name"]
        vr["_experiment_name"] = dst_experiment_name
    return src_exp_name


def do_experiments(src_experiment_name, dst_experiment_name, input_dir, output_dir):
    src_dir = mk_path(input_dir, "experiments")
    src_path = mk_path(src_dir, "experiments.json")
    src_root = io_utils.read_file(src_path)

    # Extract and update the experiment name
    dst_root = src_root.copy()
    dst_exps = dst_root["mlflow"]["experiments"]
    exp = None
    for _exp in dst_exps:
        if src_experiment_name == _exp["name"]:
            if dst_experiment_name:
                _exp["name"] = dst_experiment_name
            exp = _exp
            break
    dst_exps = [ exp ]
    dst_root["mlflow"]["experiments"] = dst_exps

    # Update experiments.json in dst root experiment dir
    dst_dir = mk_path(output_dir, "experiments")
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = mk_path(dst_dir, "experiments.json")
    io_utils.write_file(dst_path, dst_root)

    # Copy the one experiment dir
    src_exp_dir = mk_path(src_dir, exp["id"])
    dst_exp_dir = mk_path(dst_dir, exp["id"])
    shutil.copytree(src_exp_dir, dst_exp_dir)

    # Update experiment.json in dst experiment dir
    dst_exp_path = mk_path(dst_exp_dir, "experiment.json")
    dst_exp_root = io_utils.read_file(dst_exp_path)
    dst_exp = dst_exp_root["mlflow"]["experiment"]
    dst_exp["name"] = dst_experiment_name
    io_utils.write_file(dst_exp_path, dst_exp_root)


def mk_path(base_dir, path):
    return os.path.join(base_dir, path)


@click.command()
@opt_input_dir
@opt_output_dir
@click.option("--src-model",
    help="Source registered model.",
    type=str,
    required=True
)
@click.option("--dst-model",
    help="Destination registered model. If not specified use the source model.",
    type=str,
    required=False
)
@click.option("--dst-experiment",
    help="Destination experiment to update. We assum that all version runs belong to one experiment.",
    type=str,
    required=False
)
def main(input_dir, output_dir, src_model, dst_model, dst_experiment):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    do_main(input_dir, output_dir, src_model, dst_model, dst_experiment)


if __name__ == "__main__":
    main()
