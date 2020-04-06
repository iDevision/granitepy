# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------

project = 'granitepy'
copyright = 'Copyright 2020, MrRandom#9258 and twitch#7443'
author = 'MrRandom#9258 and twitch#7443'

# The full version, including alpha/beta/rc tags
release = '0.3.0a0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',

]

# Extension settings.
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
autodoc_member_order = 'groupwise'


# The suffix of source filenames.
source_suffix = '.rst'
# The master toctree document.
master_doc = 'index'

rst_prolog = """
.. |coro| replace:: This function is a |corourl|_.
.. |maybecoro| replace:: This function *could be a* |corourl|_.
.. |corourl| replace:: *coroutine*
.. _corourl: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


# -- Options for HTML output -------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'friendly'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

html_experimental_html5_writer = True

html_static_path = ['_static']
html_theme = 'alabaster'
html_theme_options = {
    "logo": "discord.png",
    "description": ""
}


