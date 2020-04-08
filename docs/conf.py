# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

# If extensions (or modules to document with) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('_extensions'))
sys.path.append(os.path.abspath('_images'))


# -- Project information -----------------------------------------------------

project = 'granitepy'
copyright = '2020, MrRandom#9258 and twitch#7443'
author = 'MrRandom#9258 and twitch#7443'

# The full version, including alpha/beta/rc tags
release = '0.4.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'builder',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'details',
    'sphinxcontrib_trio',
    'exception_hierarchy'
]

# Extension settings
autodoc_member_order = 'bysource'
autodoc_typehints = "none"

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    'typing': ('https://docs.python.org/3/', None),
    'commands': ('https://discordpy.readthedocs.io/en/latest/', None),
    'discord': ('https://discordpy.readthedocs.io/en/latest/', None),
    'aiohttp': ('https://aiohttp.readthedocs.io/en/stable/', None),
    'websockets': ('https://websockets.readthedocs.io/en/stable/', None)
}

rst_prolog = """
.. |coro| replace:: This function is a |corourl|_.
.. |maybecoro| replace:: This function *could be a* |corourl|_.
.. |corourl| replace:: *coroutine*
.. _corourl: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build']


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'friendly'


# -- Options for HTML output -------------------------------------------------

html_experimental_html5_writer = True

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
html_search_scorer = '_static/scorer.js'


# Output file base name for HTML help builder.
htmlhelp_basename = 'granitepy.pydoc'


def setup(app):
    app.add_js_file('custom.js')
