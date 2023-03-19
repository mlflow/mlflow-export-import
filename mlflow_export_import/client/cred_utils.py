""" Databricks credential utilities """

from databricks_cli.configure import provider
import os


def get_credentials(profile):
    profile = profile or get_profile()
    if profile:
        cfg = provider.get_config_for_profile(profile)
    else :
        cfg = provider.get_config() 
    return (cfg.host, cfg.token)


def get_profile(): 
    """ 
    NOTE: environment variable DATABRICKS_PROFILE doesn't exist.
    We use it specify the profile in ~/.databrickscfg.
    """
    return os.environ.get("DATABRICKS_PROFILE", None)
