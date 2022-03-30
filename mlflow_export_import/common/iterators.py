from abc import abstractmethod, ABCMeta

MAX_RESULTS = 500

class BaseIterator(metaclass=ABCMeta):
    """
    Base clase to iterate for list methods that return PageList.
    """

    @abstractmethod
    def _call_iter(self):
        pass

    @abstractmethod
    def _call_next(self):
        pass

    def __init__(self, client, max_results=MAX_RESULTS):
        self.client = client
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

class ListExperimentsIterator(BaseIterator):
    """
    Usage:
        experiments = ListExperimentssIterator(client, max_results)
        for experiment in experiments:
            print(experiment)
    """

    def _call_iter(self):
        return self.client.list_experiments(max_results=self.max_results)

    def _call_next(self):
        return self.client.list_experiments(max_results=self.max_results, page_token=self.paged_list.token)

class ListRegisteredModelsIterator(BaseIterator):
    """
    Usage:
        models = ListRegisteredModelsIterator(client, max_results)
        for model in models:
            print(model)
    """

    def _call_iter(self):
        return self.client.list_registered_models(max_results=self.max_results)

    def _call_next(self):
        return self.client.list_registered_models(max_results=self.max_results, page_token=self.paged_list.token)


class SearchRunsIterator(BaseIterator):
    def __init__(self, client, experiment_id, max_results=MAX_RESULTS, query=""):
        super().__init__(client, max_results)
        self.experiment_id = experiment_id
        self.query = query

    def _call_iter(self):
        return self.client.search_runs(self.experiment_id, self.query, max_results=self.max_results)

    def _call_next(self):
        return self.client.search_runs(self.experiment_id, self.query, max_results=self.max_results, page_token=self.paged_list.token)

class SearchRegisteredModelsIterator(BaseIterator):
    def __init__(self, client, max_results=MAX_RESULTS, query=""):
        super().__init__(client, max_results)
        self.query = query

    def _call_iter(self):
        return self.client.search_registered_models(self.query, max_results=self.max_results)

    def _call_next(self):
        return self.client.search_registered_models(self.query, max_results=self.max_results, page_token=self.paged_list.token)
