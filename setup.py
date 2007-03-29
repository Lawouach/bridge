"""
General purpose XML library based on other XML engines (Amara, xml.dom, lxml, System.Xml)
"""

#from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
from setuptools import setup
 
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']
        
setup(name = "bridge",
      version = '0.2.7',
      description = "General purpose XML library based on other XML engines (Amara, xml.dom, lxml, ElementTree, System.Xml)",
      maintainer = "Sylvain Hellegouarch",
      maintainer_email = "sh@defuze.org",
      url = "http://trac.defuze.org/wiki/bridge",
      download_url = "http://www.defuze.org/oss/bridge/",
      packages = ["bridge", "bridge.parser", "bridge.lib",
                  "bridge.filter", "bridge.validator", "bridge.test"],
      platforms = ["any"],
      license = 'BSD',
      long_description = "",
     )

