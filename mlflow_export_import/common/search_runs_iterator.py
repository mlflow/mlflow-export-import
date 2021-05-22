class SearchRunsIterator:
    """
    Usage:
        runs = SearchRunsIterator(client, exp.experiment_id, max_results)
        for run in runs:
            print(run)
    """

    def __init__(self, client, experiment_id, max_results=1000, query=""):
        self.client = client
        self.experiment_id = experiment_id
        self.max_results = max_results
        self.query = query
        self.idx = 0

    def __iter__(self):
        self.paged_list = self.client.search_runs(self.experiment_id, self.query, max_results=self.max_results)
        return self

    def __next__(self):
        if self.idx < len(self.paged_list):
            run = self.paged_list[self.idx]
            self.idx += 1
            return run
        elif self.paged_list.token is not None:
            self.paged_list = self.client.search_runs(self.experiment_id, self.query, max_results=self.max_results, page_token=self.paged_list.token)
            if len(self.paged_list) == 0:
                raise StopIteration
            self.idx = 1
            return self.paged_list[0]
        else:
            raise StopIteration
