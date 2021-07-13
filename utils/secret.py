
def load_secret(secret_name):
    with open('./secrets/'+secret_name+".secret", "r") as f:
        data = f.readline()
        return data
