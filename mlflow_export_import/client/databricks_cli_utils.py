from databricks_cli.configure import provider
from mlflow.utils.databricks_utils import is_in_databricks_runtime


def get_host_token_for_profile(profile=None):
    """
    :param profile: Databricks profile as in ~/.databrickscfg or None for the default profile
    :return: tuple of (host, token) from the ~/.databrickscfg profile
    """
    if profile:
        cfg = provider.get_config_for_profile(profile)
        if not cfg.host and is_in_databricks_runtime():
            cfg = provider.get_config() 
    else:
        cfg = provider.get_config() 
    return (cfg.host, cfg.token)


if __name__ == "__main__":
    import sys
    profile = sys.argv[1] if len(sys.argv) > 1 else None
    print("profile:",profile)
    tuple = get_host_token_for_profile(profile)
    print("host and token:", tuple)
