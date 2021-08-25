
def load_token(TEST_MODE):
    if TEST_MODE:
        return load_secret('test_token')
    else:
        return load_secret('token')


def load_secret(secret_name):
    with open('./secrets/'+secret_name+".secret", "r") as f:
        return f.readline().split('\n')[0]


def load_secrets(secret_name):
    with open('./secrets/'+secret_name+".secret", "r") as f:
        return f.read().split('\n')
