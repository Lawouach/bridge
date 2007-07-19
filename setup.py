"""
General purpose XML library for CPython and IronPython"
"""

#from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
from setuptools import setup
 
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']
        
setup(name = "bridge",
      version = '0.3.3',
      description = "General purpose XML library for CPython and IronPython",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "http://trac.defuze.org/wiki/bridge",
      download_url = "http://www.defuze.org/oss/bridge/",
      packages = ["bridge", "bridge.parser", "bridge.lib",
                  "bridge.filter", "bridge.validator"],
      platforms = ["any"],
      license = 'BSD',
      long_description = "",
     )

