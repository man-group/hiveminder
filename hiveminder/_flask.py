from __future__ import absolute_import
import os

try:
    from flask import *
except ImportError:
    # If flask isn't installed fall back to the copy in ./dependencies
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "dependencies"))
    from flask import *
    
del os
