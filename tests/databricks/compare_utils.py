def compare_experiments(exp1, exp2, client1, client2, num_runs):
    assert exp1.name == exp2.name
    _compare_experiment_tags(exp1.tags, exp2.tags)
    runs1 = client1.search_runs(exp1.experiment_id)
    runs2 = client2.search_runs(exp2.experiment_id)
    assert len(runs1) == num_runs
    assert len(runs1) == len(runs2)
    for run1,run2 in zip(runs1, runs2):
        _compare_runs(run1, run2)

def _compare_experiment_tags(tags1, tags2):
    _assert_tag("mlflow.ownerEmail", tags1, tags2)
    #_assert_tag("mlflow.experimentType", tags1, tags2) # might not be the same
    _compare_non_mlflow_tags(tags1, tags2)


def _compare_runs(run1, run2):
    _compare_non_mlflow_tags(run1.data.tags, run1.data.tags)
    assert run1.data.params == run2.data.params 
    assert run1.data.metrics == run2.data.metrics 


def _get_non_mlflow_tags(tags):
    return { k:v for k,v in tags.items() if not k.startswith("mlflow.") }

def _compare_non_mlflow_tags(tags1, tags2):
    tags1 = _get_non_mlflow_tags(tags1)
    tags2 = _get_non_mlflow_tags(tags2)
    assert tags1 == tags2

def _assert_tag(key, tags1, tags2):
    assert tags1.get(key,None) == tags2.get(key,None)
