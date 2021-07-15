
def load_secret(secret_name):
    with open('./secrets/'+secret_name+".secret", "r") as f:
        return f.readline()


def load_secrets(secret_name):
    with open('./secrets/'+secret_name+".secret", "r") as f:
        return f.read().split('\n')
