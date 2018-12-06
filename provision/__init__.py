import os
import provision
from inspect import getabsfile

def get_provision_pkg_dir():

    """Return the root directory of the provision package."""

    return os.path.dirname(getabsfile(provision))
