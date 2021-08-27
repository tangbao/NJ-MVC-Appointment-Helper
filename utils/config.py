import yaml


def load_config(logger=None):
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            if logger is not None:
                logger.error(exc)
            exit(1)

    with open("config.secret.yaml", 'r') as stream:
        try:
            secret = yaml.safe_load(stream)
            secret['admin'] = str(secret['admin'])
            secret['authorized users'] = [str(x) for x in secret['authorized users']]
        except yaml.YAMLError as exc:
            if logger is not None:
                logger.error(exc)
            exit(1)

    config.update(secret)
    return config
