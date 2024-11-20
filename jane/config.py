import pathlib
import json 

config = {}
replacements = []
port = None
host = None
upstream_host = None
upstream_port = None

def validate_config():
    if not port:
        raise AttributeError("'port' is not configured in settings.")

    if not host:
        raise AttributeError("'host' is not configured in settings.")


    if not upstream_port:
        raise AttributeError("'upstream_port' is not configured in settings.")

    if not upstream_host:
        raise AttributeError("'upstream_host' is not configured in settings.")
    if not type(patch) == list:
        raise AttributeError("'patch' is not configured as array in settings.")

def load_config(path):
    global config 
    global replacements
    path = pathlib.Path(path)
    if not path.exists():
        print("Config file {} does not exist. Exeting with 1.".format(path))
        exit(1)
    try:
        with path.open("r") as f:
            config = json.load(f)
    except Exception as ex:
        print(ex)
        print("Fatal error, probably config file invalid json. Exiting with 1.")
        exit(1)
    host = config.get('host')
    port = config.get('port')
    upstream_host = config.get('upstream_host')
    upstream_port = config.get('upstream_port')
    patch = config.get('patch',[]) 
    validate_config()

def dump_config():
    print(json.dumps(config,indent=2))
     
