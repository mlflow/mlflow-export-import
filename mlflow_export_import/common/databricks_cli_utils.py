from databricks_cli.sdk import api_client
from databricks_cli.configure import provider

''' Gets the host and token for a profile from ~/.databrickscfg '''
def get_host_token(profile=None):
  cfg = provider.get_config() if profile is None else provider.get_config_for_profile(profile)
  return (cfg.host,cfg.token)
