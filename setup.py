#!/usr/bin/python3

# Reference:
# https://docs.python.org/3.8/distutils/setupscript.html

from distutils.core import setup
import pathlib, os

# Set these variables
PACKAGE_NAME='usb-creator'
PACKAGE_DIR=PACKAGE_NAME
PACKAGE_DATA={PACKAGE_NAME: ['']}
SCRIPTS=['scripts/usb-creator']
DATA_FILES=[
    ('share/man/man1', ['man/usb-creator.1']),
    ('share/applications', ['data/usb-creator.desktop']),
    ('share/icons/hicolor/scalable/apps', ['data/usb-creator.svg']),
    ('share/usb-creator', ['data/usb-creator.glade']),
    ('share/polkit-1/actions', ['data/org.debian.pkexec.usb-creator.tmp-sh.policy']),
    ('share/solid/actions', ['data/usb-constructor-openusb.desktop'])
]

# Load the package's version.py module as a dictionary.
about = {}
here = pathlib.Path(__file__).parent.resolve()
with open(os.path.join(here, 'version.py')) as f:
    exec(f.read(), about)
    
# Get the long description from the README file
try:
    long_description = (here / 'README.md').read_text(encoding='utf-8')
except FileNotFoundError:
    long_description = about['__description__']
    
setup(
    # Meta data
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    url=about['__url__'],
    description=about['__description__'],
    long_description=long_description,
    download_url=about['__download_url__'],
    # Classifiers help users find your project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3.
        'Programming Language :: Python :: 3'
    ],
    platforms   = 'POSIX',
    license     = 'GNU General Public License v2 or later (GPLv2+)',
    
    # Package data
    packages=[PACKAGE_NAME],
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    package_data=PACKAGE_DATA,
    scripts=SCRIPTS,
    data_files=DATA_FILES
)
