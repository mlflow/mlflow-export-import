"""
Run dump utilities.
"""

import time
import click
import mlflow

INDENT = "  "
MAX_LEVEL = 1
TS_FORMAT = "%Y-%m-%d_%H:%M:%S"
client = mlflow.tracking.MlflowClient()
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

def dump_run(run, max_level=1, indent=""):
    dump_run_info(run.info,indent)
    print(indent+"Params:")
    for k,v in sorted(run.data.params.items()):
        print(indent+"  {}: {}".format(k,v))
    print(indent+"Metrics:")
    for k,v in sorted(run.data.metrics.items()):
        print(indent+"  {}: {}".format(k,v))
    print(indent+"Tags:")
    for k,v in sorted(run.data.tags.items()):
        print(indent+"  {}: {}".format(k,v))
    print("{}Artifacts:".format(indent))
    num_bytes, num_artifacts = dump_artifacts(run.info.run_id, "", 0, max_level, indent+INDENT)
    print(f"{indent}Total: bytes: {num_bytes} artifacts: {num_artifacts}")
    return run, num_bytes, num_artifacts
        
def dump_run_id(run_id, max_level=1, indent=""):
    run = client.get_run(run_id)
    return dump_run(run,max_level,indent)

def dump_run_info(info, indent=""):
    print("{}RunInfo:".format(indent))
    exp = client.get_experiment(info.experiment_id)
    if exp is None:
        print(f"ERROR: Cannot find experiment ID '{info.experiment_id}'")
        return 
    print("{}  name: {}".format(indent,exp.name))
    for k,v in sorted(info.__dict__.items()):
        if not k.endswith("_time"):
            print("{}  {}: {}".format(indent,k[1:],v))
    start = _dump_time(info,'_start_time',indent)
    end = _dump_time(info,'_end_time',indent)
    if start is not None and end is not None:
        dur = float(end - start)/1000
        print("{}  _duration:  {} seconds".format(indent,dur))

def _dump_time(info, k, indent=""):
    v = info.__dict__.get(k,None)
    if v is None:
        print("{}  {:<11} {}".format(indent,k[1:]+":",v))
    else:
        stime = time.strftime(TS_FORMAT,time.gmtime(v/1000))
        print("{}  {:<11} {}   {}".format(indent,k[1:]+":",stime,v))
    return v

def dump_artifacts(run_id, path, level, max_level, indent):
    if level+1 > max_level: 
        return 0,0
    artifacts = client.list_artifacts(run_id,path)
    num_bytes, num_artifacts = (0,0)
    for j,art in enumerate(artifacts):
        print("{}Artifact {}/{} - level {}:".format(indent,j+1,len(artifacts),level))
        num_bytes += art.file_size or 0
        print(f"  {indent}path: {art.path}")
        if art.is_dir:
            b,a = dump_artifacts(run_id, art.path, level+1, max_level, indent+INDENT)
            num_bytes += b
            num_artifacts += a
        else:
            print(f"  {indent}bytes: {art.file_size}")
            num_artifacts += 1
    return num_bytes,num_artifacts

@click.command()
@click.option("--run-id", help="Run ID.", required=True)
@click.option("--artifact-max-level", help="Number of artifact levels to recurse.", default=1, type=int)

def main(run_id, artifact_max_level):
    print("Options:")
    for k,v in locals().items(): print(f"  {k}: {v}")
    dump_run_id(run_id, artifact_max_level)

if __name__ == "__main__":
    main()
