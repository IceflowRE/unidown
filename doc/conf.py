import sys
from pathlib import Path

import sphinx_rtd_theme

sys.path.insert(0, str(Path('../').resolve()))
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'

project = 'Universal Downloader'
author = 'Iceflower S'
copyright = '2015-present, Iceflower S'
title = project + ' Documentation'
# TODO
version = '2.0.3'
release = '2.0.3'

language = 'english'
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_css_files = [
    'css/style.css',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'urllib3': ('https://urllib3.readthedocs.io/en/latest/', None),
    'packaging': ('https://packaging.pypa.io/en/latest/', None),
}

# sphinx.ext.todo
todo_include_todos = True

# sphinx.ext.autodoc
autodoc_inherit_docstrings = False
always_document_param_types = True
add_module_names = False
autodoc_default_options = {
    'members': True,
    'member-order': "groupwise",
    'private-members': True,
    'show-inheritance': True,
    'special-members': False,
    'undoc-members': True,
    'exclude-members': ','.join([])
}

# sphinx.ext.autosummary
autosummary_ignore_module_all = True
autosummary_imported_members = False
