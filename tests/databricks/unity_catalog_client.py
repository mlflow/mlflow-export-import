class UnityCatalogClient:
    def __init__(self, dbx_client):
        self.client = mk_uc_dbx_client(dbx_client)

    def list_models(self, catalog_name=None, schema_name=None):
        if catalog_name and schema_name:
            params = { "catalog_name": catalog_name, "schema_name": schema_name }
        else:
            params = { "max_results": 5000 }
        rsp = self.client.get("unity-catalog/models", params)
        if len(rsp) == 0:
            return rsp
        return rsp["registered_models"]

    def list_model_names(self, catalog_name, schema_name):
        return [ m["full_name"] for m in self.list_models(catalog_name, schema_name) ]

    def create_schema(self, catalog_name, schema_name):
        params = { "catalog_name": catalog_name, "name": schema_name }
        self.client.post("unity-catalog/schemas", params)

    def __repr__(self):
        return str(self.client)


def mk_uc_dbx_client(client):
    from mlflow_export_import.client.http_client import HttpClient
    return HttpClient("api/2.1", client.host, client.token)
