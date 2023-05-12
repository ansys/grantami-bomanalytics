import sys
import os
from datetime import datetime
from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black
import shutil
from pathlib import Path
import jupytext

sys.path.insert(0, os.path.abspath("../../src"))
from ansys.grantami.bomanalytics import __version__


# -- Project information -----------------------------------------------------

project = "ansys.grantami.bomanalytics"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."
html_title = f"PyGranta BoM Analytics {__version__}"

# The short X.Y version
release = version = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "notfound.extension",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.extlinks",
    "sphinx.ext.coverage",
    "enum_tools.autoenum",
    "nbsphinx",
]

# sphinx
add_module_names = False

# sphinx.ext.autodoc
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_type_aliases = {"Yaml": "Yaml"}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    "openapi-common": ("https://openapi.docs.pyansys.com", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# static path
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/dataframe.css",
]
html_js_files = [
    "js/add_blank.js",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

rst_epilog = """
.. |WatchListIndicator| replace:: :class:`~ansys.grantami.bomanalytics.indicators.WatchListIndicator`
.. |RoHSIndicator| replace:: :class:`~ansys.grantami.bomanalytics.indicators.RoHSIndicator`
"""

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "_templates", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True


# -- Options for HTML output -------------------------------------------------
cname = os.getenv("DOCUMENTATION_CNAME", "bomanalytics.grantami.docs.pyansys.com")
"""The canonical name of the webpage hosting the documentation."""
html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon
html_logo = pyansys_logo_black
html_theme_options = {
    "github_url": "https://github.com/pyansys/grantami-bomanalytics",
    "additional_breadcrumbs": [
        ("PyAnsys Documentation", "https://docs.pyansys.com/"),
        ("PyGranta", "https://grantami.docs.pyansys.com/"),
    ],
    "show_breadcrumbs": True,
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "pybomanalyticsdoc"


# -- Options for LaTeX output ------------------------------------------------
latex_elements = {"extraclassoptions": "openany,oneside"}
latex_engine = "xelatex"

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("latexindex", "pyansys.tex", "ansys.grantami.bomanalytics Documentation", author, "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        master_doc,
        "ansys.grantami.bomanalytics",
        "ansys.grantami.bomanalytics Documentation",
        [author],
        1,
    )
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "ansys.grantami.bomanalytics",
        "ansys.grantami.bomanalytics Documentation",
        author,
        "ansys.grantami.bomanalytics",
        "Python interface to the Granta MI Restricted Substances module",
        "Engineering Software",
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Example Script functions -------------------------------------------------

# Define some important paths and check were are where we expect to be
cwd = Path(os.getcwd())
assert cwd.name == "source"
EXAMPLES_DIR_NAME = "examples"
DUMMY_EXAMPLES_DIR_NAME = "examples-dummy"

examples_output_dir = Path(EXAMPLES_DIR_NAME).absolute()
examples_source_dir = Path("../../" + EXAMPLES_DIR_NAME).absolute()
dummy_examples_source_dir = Path("../../" + DUMMY_EXAMPLES_DIR_NAME).absolute() / Path(EXAMPLES_DIR_NAME)
EXAMPLE_FLAG = os.getenv("BUILD_EXAMPLES")

# If we are building examples, use the included ipython-profile
if EXAMPLE_FLAG:
    ipython_dir = Path("../../.ipython").absolute()
    os.environ["IPYTHONDIR"] = str(ipython_dir)


def _copy_examples_and_convert_to_notebooks(source_dir, output_dir):
    for root, dirs, files in os.walk(source_dir):
        root_path = Path(root)
        index = root_path.parts.index(EXAMPLES_DIR_NAME) + 1  # Path elements below examples
        root_output_path = output_dir.joinpath(*root_path.parts[index:])
        root_output_path.mkdir(parents=False, exist_ok=False)  # Create new folders in corresponding output location
        for file in files:
            file_source_path = root_path / Path(file)
            file_output_path = root_output_path / Path(file)
            shutil.copy(file_source_path, file_output_path)  # Copy everything
            if file_source_path.suffix == ".py":  # Also convert python scripts to jupyter notebooks
                ntbk = jupytext.read(file_source_path)
                jupytext.write(ntbk, file_output_path.with_suffix(".ipynb"))


# If we already have a source/examples directory then don't do anything.
# If we don't have an examples folder, we must first create it
# We don't delete the examples after every build because this triggers nbsphinx to re-run them, which is very expensive
# Run `make clean` to force a rebuild, which will delete the 'examples' output folder and reset this choice
if not examples_output_dir.is_dir():
    # Only include examples if the environment variable is set to something truthy
    if EXAMPLE_FLAG:
        print("'BUILD_EXAMPLES' environment variable is set, including examples in docs build.")
        _copy_examples_and_convert_to_notebooks(examples_source_dir, examples_output_dir)

    # If we are skipping examples in the docs, create a placeholder index.rst file to avoid sphinx errors.
    else:
        print("'BUILD_EXAMPLES' environment variable is not set, using standalone examples.")
        _copy_examples_and_convert_to_notebooks(dummy_examples_source_dir, examples_output_dir)


nbsphinx_prolog = """
Download this example as a :download:`Jupyter notebook </{{ env.docname }}.ipynb>` or a
:download:`Python script </{{ env.docname }}.py>`.

----
"""
