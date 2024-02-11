from packaging import version
import mlflow


class BaseIterator():
    """
    Base class to iterate for 'search' methods that return PageList.
    """
    def __init__(self, search_method, max_results=None, filter=None):
        self.search_method = search_method
        self.filter = filter
        self.max_results = max_results
        self.idx = 0
        self.paged_list = None
        self.kwargs = { "max_results": self.max_results } if self.max_results else {}

    def _call_iter(self):
        if version.parse(mlflow.__version__) < version.parse("2.2.1"):
            return self.search_method(filter_string=self.filter)  #7623 - https://mlflow.org/docs/2.1.1/python_api/mlflow.client.html
        else:
            return self.search_method(filter_string=self.filter, **self.kwargs) # https://mlflow.org/docs/latest/python_api/mlflow.client.html

    def _call_next(self):
        return self.search_method(filter_string=self.filter, page_token=self.paged_list.token, **self.kwargs)

    def __iter__(self):
        self.paged_list = self._call_iter()
        return self

    def __next__(self):
        if self.idx < len(self.paged_list):
            chunk = self.paged_list[self.idx]
            self.idx += 1
            return chunk
        elif self.paged_list.token is None or self.paged_list.token == "":
            raise StopIteration
        else:
            self.paged_list = self._call_next()
            if len(self.paged_list) == 0:
                raise StopIteration
            self.idx = 1
            return self.paged_list[0]


class SearchExperimentsIterator(BaseIterator):
    """
    Usage:
        experiments = SearchExperimentsIterator(client, max_results)
        for experiment in experiments:
            print(experiment)
    """
    def __init__(self, client, view_type=None, max_results=None, filter=None):
        super().__init__(client.search_experiments, max_results=max_results, filter=filter)
        if view_type:
            self.kwargs["view_type"] = view_type


class SearchRegisteredModelsIterator(BaseIterator):
    """
    Usage:
        models = SearchRegisteredModelsIterator(client, max_results)
        for model in models:
            print(model)
    """
    def __init__(self, client, max_results=None, filter=None):
        super().__init__(client.search_registered_models, max_results=max_results, filter=filter)


class SearchModelVersionsIterator(BaseIterator):
    """
    Usage:
        versions = SearchModelVersionsIterator(client)
        for vr in versions:
            print(vr)
    """
    def __init__(self, client, max_results=None, filter=None):
        super().__init__(client.search_model_versions, max_results=max_results, filter=filter)


class SearchRunsIterator(BaseIterator):
    def __init__(self, client, experiment_ids, max_results=None, filter=None, view_type=None):
        super().__init__(client.search_runs, max_results=max_results, filter=filter)
        self.kwargs["experiment_ids"] = experiment_ids
        if view_type:
            self.kwargs["run_view_type"] = view_type
