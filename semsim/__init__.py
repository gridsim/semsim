import pkg_resources  # part of setuptools
__version__ = pkg_resources.require("SemSim")[0].version
