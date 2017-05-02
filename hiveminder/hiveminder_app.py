from __future__ import absolute_import
from .app import app, _PORT
from .game_api import *
from .algo_api import *

import os
import webbrowser
import subprocess
import platform


def browser(hostname, port, debug):
    if 'SUPPRESS_BROWSER_START' not in os.environ:
        if debug:
            # If we have reloading turned on, suppress future browser starts
            os.environ['SUPPRESS_BROWSER_START'] = ""
        webbrowser.open_new_tab("http://{}:{}".format(hostname, port))


def start_other(hostname, port, debug, open_browser):
    if open_browser:
        browser(hostname, port, debug)
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host=hostname,
            port=port,
            debug=debug)


def is_nginx_up():
    if platform.python_version_tuple()[0] == '2':
        from urllib2 import urlopen, URLError
    else:
        from urllib.request import urlopen
        from urllib.error import URLError
    try:
        urlopen("http://localhost:{}/".format(_PORT)).close()
    except URLError:
        return False
    return True


def start_windows(debug, open_browser):
    nginx_dir = os.path.join(os.path.dirname(__file__), "dependencies", "nginx")
    nginx_exe = os.path.join(nginx_dir, "nginx.exe")

    if not is_nginx_up():
        subprocess.Popen(nginx_exe, cwd=nginx_dir)

    try:
        from flup.server.fcgi import WSGIServer
    except ImportError:
        # If flup isn't installed fall back to the copy in ./dependencies
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies"))
        from flup.server.fcgi import WSGIServer

    if open_browser:
        browser('localhost', _PORT, debug)
    WSGIServer(app, debug=debug, bindAddress=('localhost', _PORT + 1)).run()


def start_gunicorn(hostname, port, open_browser):
    import sys
    try:
        from gunicorn.app.wsgiapp import WSGIApplication
    except ImportError:
        # If gunicorn isn't installed fall back to the copy in ./dependencies
        sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies"))
        from gunicorn.app.wsgiapp import WSGIApplication

    if open_browser:
        browser('localhost', port, False)
    
    sys.argv = [sys.argv[0]] + ["--bind", "{}:{}".format(hostname, port),
                                "--workers", "1",
                                "--threads", "1",
                                "uwsgi:app",
                                os.path.join(os.path.dirname(__file__), "app.py")]
    
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
    

def start(hostname='localhost', port=_PORT, debug=True, open_browser=True):
    if (platform.system() == "Windows"
        and hostname == 'localhost'
        and port == _PORT):
        start_windows(debug, open_browser)
    elif platform.system() in ("Linux", "Darwin"):
        start_gunicorn(hostname, port, open_browser)
    else:
        start_other(hostname, port, debug, open_browser)
