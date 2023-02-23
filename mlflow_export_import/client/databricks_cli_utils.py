from databricks_cli.configure import provider

def get_host_token(profile=None):
    """ Get the host and token for a profile from ~/.databrickscfg. """
    cfg = provider.get_config() if profile is None else provider.get_config_for_profile(profile)
    return (cfg.host,cfg.token)
