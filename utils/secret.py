
def load_secret(secret_name):
    with open(secret_name+".secret", "r") as f:
        data = f.readline()
        return data
