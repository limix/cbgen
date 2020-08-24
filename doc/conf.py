import datetime

import cbgen

# -- Project information -----------------------------------------------------

now = datetime.datetime.now()
project = "cbgen"
copyright = f"{now.year}, Danilo Horta"
author = "Danilo Horta"

# The full version, including alpha/beta/rc tags
release = cbgen.__version__
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

autosummary_generate = True
napoleon_numpy_docstring = True
napoleon_use_rtype = False
pygments_style = "default"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "style_external_links": True,
}

intersphinx_mapping = {
    "https://docs.python.org/": None,
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
}
