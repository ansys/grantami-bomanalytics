import datetime
import os
from pathlib import Path
import shutil
import sys

from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black
import jupytext
from sphinx.application import Sphinx

from ansys.grantami.bomanalytics import __version__

sys.path.insert(0, os.path.abspath("../"))
from class_documenter import ClassDocumenter

sys.path.insert(0, os.path.abspath("../../src"))

# Project information
project = "ansys-grantami-bomanalytics"
now = datetime.datetime.now()
project_copyright = f"(c) {now.year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
switcher_version = get_version_match(version)

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = f"PyGranta BoM Analytics {__version__}"
html_favicon = ansys_favicon

cname = os.getenv("DOCUMENTATION_CNAME", "bomanalytics.grantami.docs.pyansys.com")
"""The canonical name of the webpage hosting the documentation."""

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/grantami-bomanalytics",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyGranta", "https://grantami.docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": True,
}

linkcheck_ignore = []
# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/grantami-bomanalytics/releases/tag/v{__version__}"
    )

extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.doctest",
    "notfound.extension",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.extlinks",
    "sphinx.ext.coverage",
    "nbsphinx",
    "sphinx_design",
]

# sphinx
add_module_names = False
nitpick_ignore = [
    # Ignore "Query Result", the type of the Returns section of client.run()
    ("py:obj", "Query"),
    ("py:obj", "Result"),
    # Ignore `available_flags` on indicator classes, as sphinx seems to struggle with a type as a class attribute. The
    # link is generated correctly, but a warning is emitted.
    ('py:obj', 'available_flags'),
]

# sphinx.ext.autodoc
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.11", None),
    "openapi-common": ("https://openapi.docs.pyansys.com/version/stable", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {
    "optional",
    "_FinalAttributeReferenceBuilder",
    "_FinalRecordReferenceBuilder",
    "_AttributeReferenceByNameBuilder",
}

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
# Ignore missing docstring warning on dataclasses parameters.
numpydoc_validation_exclude = {
    r"^ansys\.grantami\.bomanalytics\.bom_types\.[\w]+\.[\w]+\.[\w]+$"
}

extlinks = {
    'MI_docs': (
        'https://ansyshelp.ansys.com/public/account/secured?returnurl=/Views/Secured/Granta/v252/en/Granta_MI/%s',
        None
    ),
    "OpenAPI-Common": ("https://openapi.docs.pyansys.com/version/stable/%s", None),
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


def setup(app: Sphinx):
    # Register custom documenter as the default documenter for classes.
    app.add_autodocumenter(ClassDocumenter, override=True)
