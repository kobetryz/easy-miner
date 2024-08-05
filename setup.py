import sys
from setuptools import setup
sys.setrecursionlimit(5000)
APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygments', 'cytoolz'],
    'includes': ['pygments.lexers', 'pygments.formatters', 'pygments.styles', 'cytoolz.functoolz'],
    'excludes': ['PyInstaller']
}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
