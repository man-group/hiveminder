from hiveminder.hiveminder_app import start, app
from algos import *

if __name__ == '__main__':
    start(hostname="0.0.0.0",
          port=5000,
          debug=False,
          open_browser=False)
