from databricks_cli.configure import provider


def get_host_token(profile=None):
    """
    :param profile: as in ~/.databrickscfg or 'None' for the default profile
    :return: tuple of host and token per ~/.databrickscfg profile
    """
    if profile:
        cfg = provider.get_config_for_profile(profile)
    else:
        cfg = provider.get_config() 
    return (cfg.host, cfg.token)


if __name__ == "__main__":
    import sys
    profile = sys.argv[1] if len(sys.argv) > 1 else None
    print("profile:",profile)
    tuple = get_host_token(profile)
    print("host/token:", tuple)
