import os, glob


def _get_algo_info():
    modules = list(sorted(glob.glob(os.path.join(os.path.dirname(__file__),
                                    "*.py"))))
    ctimes = {f: os.path.getctime(f) for f in modules}
    fsizes = {f: os.path.getsize(f) for f in modules}
    return modules, ctimes, fsizes


modules, ctimes, fsizes = _get_algo_info()
__all__ = [os.path.basename(f)[:-3] for f in modules if not f=="__init__.py"]


try:
    import uwsgi
except ImportError:
    pass
else:
    # Poll algo files every second and reload if any of them change
    def check_for_new(signum):
        if (modules, ctimes, fsizes) != _get_algo_info():
            uwsgi.reload()

    try:
        uwsgi.register_signal(13, 'workers', check_for_new)
        uwsgi.add_timer(13, 1)
    except AttributeError:
        pass
    except ValueError:
        pass
