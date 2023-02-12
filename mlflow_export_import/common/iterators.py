from abc import abstractmethod, ABCMeta
from mlflow.entities import ViewType

MAX_RESULTS = 500

class BaseIterator(metaclass=ABCMeta):
    """
    Base class to iterate for list methods that return PageList.
    """

    @abstractmethod
    def _call_iter(self):
        pass

    @abstractmethod
    def _call_next(self):
        pass

    def __init__(self, client, max_results=MAX_RESULTS, filter=None):
        self.client = client
        self.filter = filter
        self.max_results = max_results
        self.idx = 0
        self.paged_list = None

    def __iter__(self):
        self.paged_list = self._call_iter()
        return self

    def __next__(self):
        if self.idx < len(self.paged_list):
            model = self.paged_list[self.idx]
            self.idx += 1
            return model
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
        super().__init__(client, max_results, filter)
        self.view_type = view_type

    def _call_iter(self):
        return self.client.search_experiments(max_results=self.max_results, filter_string=self.filter, view_type=self.view_type)

    def _call_next(self):
        return self.client.search_experiments(max_results=self.max_results, page_token=self.paged_list.token, filter_string=self.filter, view_type=self.view_type)



class SearchRunsIterator(BaseIterator):
    def __init__(self, client, experiment_id, max_results=MAX_RESULTS, filter=None):
        super().__init__(client, max_results, filter)
        self.experiment_id = experiment_id

    def _call_iter(self):
        return self.client.search_runs(self.experiment_id, self.filter, max_results=self.max_results)

    def _call_next(self):
        return self.client.search_runs(self.experiment_id, self.filter, max_results=self.max_results, page_token=self.paged_list.token)


class SearchRegisteredModelsIterator(BaseIterator):
    """
    Usage:
        models = SearchRegisteredModelsIterator(client, max_results)
        for model in models:
            print(model)
    """
    def __init__(self, client, max_results=MAX_RESULTS, filter=None):
        super().__init__(client, max_results, filter)

    def _call_iter(self):
        return self.client.search_registered_models(self.filter, max_results=self.max_results)

    def _call_next(self):
        return self.client.search_registered_models(self.filter, max_results=self.max_results, page_token=self.paged_list.token)


class SearchModelVersionsIterator(BaseIterator):
    """
    Usage:
        models = SearchRegisteredModelsIterator(client)
        for model in models:
            print(model)
    """
    def __init__(self, client, filter=None):
        super().__init__(client, filter=filter)

    def _call_iter(self):
        return self.client.search_model_versions(self.filter)

    def _call_next(self):
        return self.client.search_model_versions(self.filter, page_token=self.paged_list.token)
