
from distutils.core import setup, Extension

pyclamd = Extension('pyclamd',
                    sources = ['pyclamd.py'])

# Install : python setup.py install
# Register : python setup.py register

try:
    import pyclamd
except ImportError as x:
    # all we want is the version
    pyclamd.__version__ = 'unknown'


setup (name = 'pyClamd',
       version = pyclamd.__version__,
       download_url = 'http://xael.org/norman/python/pyclamd/',
       package_dir={'pyclamd': ''},
       packages=['pyclamd'],

       license ='License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
       author = 'Alexandre Norman',
       author_email = 'norman()xael.org',
       keywords='python, clamav, antivirus, scanner, virus, libclamav',
       url = 'http://xael.org/norman/python/pyclamd/',
       include_dirs = ['/usr/local/include'],
       description = 'pyClamd is a python interface to Clamd (Clamav daemon).',
       long_description = 'pyClamd is a python interface to Clamd (Clamav daemon). By using pyClamd, you can add virus detection capabilities to your python software in an efficient and easy way. Instead of pyClamav which uses libclamav, pyClamd may be used by a closed source product.',
       classifiers=[
           'Development Status :: 5 - Production/Stable',
           'Programming Language :: Python',
           'Environment :: Console',
           'Intended Audience :: Developers',
           'Intended Audience :: System Administrators',
           'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
           'Operating System :: OS Independent',
           'Topic :: System',
           'Topic :: Security',
           ],
       )
