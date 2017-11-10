import sys
from pathlib import Path

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.coverage',
              'sphinx.ext.ifconfig',
              'sphinx.ext.viewcode']

sys.path.insert(0, str(Path('../../').resolve()))

source_suffix = ['.rst', '.md']
master_doc = 'index'

project = 'Universal-Downloader'
copyright = '2017, Iceflower S'
author = 'Iceflower S'
version = '2.0.0'
release = '2.0.0'

language = None
exclude_patterns = []
pygments_style = 'sphinx'
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'urllib3': ('https://urllib3.readthedocs.io/en/latest/', None),
    'packaging': ('https://packaging.pypa.io/en/latest/', None),
}

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'universal-downloader', 'Universal-Downloader Documentation',
     [author], 1)
]
