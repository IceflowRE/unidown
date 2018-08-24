import sys
from pathlib import Path

import sphinx_rtd_theme

sys.path.insert(0, str(Path('../../').resolve()))
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.ifconfig',
              'sphinx.ext.imgmath',
              'sphinx.ext.viewcode',
              ]
              #'sphinxcontrib.inkscapeconverter',]
source_suffix = '.rst'
master_doc = 'index'

project = 'Universal Downloader'
author = 'Iceflower S'
copyright = '2018, Iceflower S'
title = project + ' Documentation'
version = '2.0.0'
release = '2.0.0'

language = None  # english
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
man_pages = [
    (master_doc, project, title,
     [author], 1)
]

imgmath_latex = r'latex'
imgmath_dvisvgm = r'dvisvgm'
imgmath_font_size = 14

inkscape_converter_bin = r'inkscape'

latex_elements = {
    # Additional stuff for the LaTeX preamble.
    'preamble': r'''
\newcommand*{\fontPath}{../../fonts/} % font __path

\usepackage{fontspec} % set fonts
\setmainfont[ % main font: no serif!
Path           = \fontPath/NotoSans/,
Extension      = .ttf,
Ligatures      = TeX,
BoldFont       = NotoSans-Bold,
ItalicFont     = NotoSans-Italic,
BoldItalicFont = NotoSans-BoldItalic
]{NotoSans-Regular}
\setsansfont[ % sans font
Path           = \fontPath/NotoSans/,
Extension      = .ttf,
Ligatures      = TeX,
BoldFont       = NotoSans-Bold,
ItalicFont     = NotoSans-Italic,
BoldItalicFont = NotoSans-BoldItalic
]{NotoSans-Regular}
\setmonofont[ % mono font
Path           = \fontPath/NotoMono/,
Extension      = .ttf,
Ligatures      = TeX,
]{NotoMono-Regular}

%\usepackage{unicode-math}
%\setmathfont{Latin Modern Math}[Scale=MatchLowercase]
%\setmathrm{Latin Modern Roman}[Scale=MatchLowercase]

\renewcommand*{\glqq}{\quotedblbase} % tell NotoSans what german quotes are
\renewcommand*{\grqq}{\textquotedblleft} % tell NotoSans what german quotes are

\usepackage{geometry}
\geometry{
    a4paper,
    top=2cm,
    left=2cm,
    right=2cm,
    bottom=2cm,
}
\def\arraystretch{1.5}% increase space btw lines and text

\usepackage{xcolor} % colors
\definecolor{blazeOrange}{HTML}{FF6803} % internal pdf linking
\definecolor{blueRibbon}{HTML}{0368FF} % url links

\usepackage{hyperref} % pdf metadata and linking
\hypersetup{
    pdftitle={''' + title + '''},
    pdfauthor={''' + author + r'''},
    breaklinks=true,
    linktocpage=false,
    linkcolor=blazeOrange,
    citecolor=blazeOrange,
    urlcolor=blueRibbon,
    colorlinks=true,
    linkbordercolor = white,
    urlbordercolor = white,
    citebordercolor = white, 
}
\usepackage{caption} % fixes correct linking of hyperref

\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000

\makeatletter
\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\makeatother
''',
}
latex_documents = [('index',
                    'sphinx.tex',
                    title,
                    author,
                    'scrreprt',
                    False)]
latex_paper_size = "A4"
imgmath_image_format = 'svg'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'urllib3': ('https://urllib3.readthedocs.io/en/latest/', None),
    'packaging': ('https://packaging.pypa.io/en/latest/', None),
}
