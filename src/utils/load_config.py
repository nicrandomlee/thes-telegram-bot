import yaml
import json

def concat(loader, node):
    seq = loader.construct_sequence(node)
    return "".join([str(i) for i in seq])

yaml.add_constructor("!concat", concat)

def load_config(filepath):
    if ".json" in filepath:
        with open(filepath, "r") as stream:
            config = json.load(stream)

    elif ".yml" in filepath:
        with open(filepath, "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    elif ".yaml" in filepath:
        with open(filepath, "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    else:
        raise Exception("File extension not supported.")
    
    return config
    