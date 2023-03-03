from mlflow.entities import ViewType
import mlflow

MAX_RESULTS = 500


class BaseIterator():
    """
    Base class to iterate for list methods that return PageList.
    """

    def _call_iter(self):
        if mlflow.__version__ < "2.2.1": 
            return self.method(self.filter)  #7623 - https://mlflow.org/docs/2.1.1/python_api/mlflow.client.html
        else:
            return self.method(self.filter, max_results=self.max_results) # https://mlflow.org/docs/latest/python_api/mlflow.client.html

    def _call_next(self):
        return self.method(self.filter, max_results=self.max_results, page_token=self.paged_list.token)

    def __init__(self, method, max_results=MAX_RESULTS, filter=None):
        self.method = method
        self.filter = filter
        self.max_results = max_results
        self.idx = 0
        self.paged_list = None

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

    def __init__(self, client, view_type=ViewType.ACTIVE_ONLY, max_results=MAX_RESULTS, filter=None):
        super().__init__(client.search_experiments, max_results, filter)
        self.view_type = view_type


class SearchRegisteredModelsIterator(BaseIterator):
    """
    Usage:
        models = SearchRegisteredModelsIterator(client, max_results)
        for model in models:
            print(model)
    """
    def __init__(self, client, max_results=MAX_RESULTS, filter=None):
        super().__init__(client.search_registered_models, max_results, filter)


class SearchModelVersionsIterator(BaseIterator):
    """
    Usage:
        versions = SearchModelVersionsIterator(client)
        for vr in versions:
            print(vr)
    """
    def __init__(self, client, max_results=MAX_RESULTS, filter=None):
        super().__init__(client.search_model_versions, max_results=max_results, filter=filter)


class SearchRunsIterator(BaseIterator):
    def __init__(self, client, experiment_id, max_results=MAX_RESULTS, filter=None):
        super().__init__(None, max_results, filter)
        self.experiment_id = experiment_id
        self.client = client

    def _call_iter(self):
        return self.client.search_runs(self.experiment_id, filter_string=self.filter, max_results=self.max_results)

    def _call_next(self):
        return self.client.search_runs(self.experiment_id, filter_string=self.filter, max_results=self.max_results, page_token=self.paged_list.token)

