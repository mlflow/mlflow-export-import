""" Databricks credential utilities """

from databricks_cli.configure import provider

def get_credentials(profile):
    cfg = provider.get_config() if profile is None else provider.get_config_for_profile(profile)
    return (cfg.host, cfg.token)
