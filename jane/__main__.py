import sys 
from jane import config
from jane import app

if __name__ == '__main__':
    print("Config file:",sys.argv[1])
    config.load_config(sys.argv[1])
    app.main()
