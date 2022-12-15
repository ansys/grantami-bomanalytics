# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Basic usage example

# This example shows how to connect to Granta MI and perform a basic query for impacted substances. It also
# demonstrates how to view logging messages returned by the Granta MI server. For more information about the
#  results of the queries, see the examples in [Impacted Substances](1_Impacted_Substances_Queries/index.rst) and
# [Compliance](2_Compliance_Queries/index.rst).

# ## Connect to Granta MI

# First, use the ``ansys.grantami.bomanalytics.Connection`` class to connect to the Granta MI server. The ``Connection``
# class uses a fluent interface to build the connection, which is always invoked in the following sequence:
#
# 1. Specify your Granta MI Service Layer URL as a parameter to the ``Connection`` class.
# 2. Specify the authentication method using a ``Connection.with_...()`` method.
# 3. Use the ``Connection.connect()`` method to finalize the connection.
#
# This returns a connection object, which is called ``cxn`` in these examples.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
# -

# If you are running your Python script on Windows, you are generally able to use ``.with_autologon()``.

# + tags=[]
cxn = Connection(server_url).with_autologon().connect()
cxn
# -

# If the Python script is running on Linux without Kerberos enabled, or you want to use an account other than your
# logged-in account, you can specify credentials explicitly.

# + tags=[]
cxn = Connection(server_url).with_credentials("my_username", "my_password").connect()
cxn
# -

# OIDC and anonymous authentication methods are also available, but they are beyond the scope of this example.
# For more information, see the [ansys-openapi-common](https://github.com/pyansys/openapi-common) package
# documentation.

# ## Construct a query

# Queries are also constructed using a fluent interface. However, the ``Query`` constructor takes no arguments. All
# query details are specified using ``Query`` methods. To demonstrate this, this example builds a query to
# determine all substances present in an ABS material that are impacted by the REACH Candidate List legislation.

# First import the ``queries`` module and create a ``MaterialImpactedSubstancesQuery`` object.

# + tags=[]
from ansys.grantami.bomanalytics import queries

query = queries.MaterialImpactedSubstancesQuery()
query
# -

# Now add the material that you want to query by specifying its naterial ID. (Alternate methods of specifying records
# are shown in other examples.)

# + tags=[]
query = query.with_material_ids(["plastic-abs-high-impact"])
query
# -

# Note that because the ``MaterialImpactedSubstancesQuery`` object has a fluent interface, you receive the same object
# back that you started with, but with the material IDs added.
#
# Finally, add the legislation to the query.

# + tags=[]
query = query.with_legislations(["REACH - The Candidate List"])
query
# -

# Fluent interfaces are designed to allow a complex object to be constructed in a single line of code. As such, you can
# consolidate the cells above into a single step:

# + tags=[]
query = queries.MaterialImpactedSubstancesQuery().with_material_ids(["plastic-abs-high-impact"]).with_legislations(["REACH - The Candidate List"])  # noqa: E501
query
# -

# Because the fluent interface can produce very long lines of code, it's necessary to break your query creation code
# into multiple lines. The following multi-line format is used throughout the examples. It is functionally equivalent to
# the preceding cell:

# + tags=[]
query = (
    queries.MaterialImpactedSubstancesQuery()
    .with_material_ids(["plastic-abs-high-impact"])
    .with_legislations(["REACH - The Candidate List"])
)
query
# -

# The multi-line format is the recommended way of creating queries using this API.

# ## Run a query

# Now that you have your ``cxn`` and ``query`` objects, you can use the ``cxn.run()`` method to run the query. This
# returns an object that contains the results of the query.

# + tags=[]
result = cxn.run(query)
result
# -

# ## View query results

# In the case of ``MaterialsImpactedSubstancesQuery``, the results object contains the list of substances present in
# the material that are impacted by the specified legislations.

# + tags=[]
result.impacted_substances
# -

# ## View logged messages

# All query results also contain a list of messages returned by the server while running the query. These are
# sorted in order of decreasing severity. The same messages are also available in the MI Service Layer log file.

# + tags=[]
result.messages
# -

# Additionally, these messages are available via the standard ``logging`` module using the
# ``ansys.grantami.bomanalytics`` logger. Alternatively, you can omit the logger name to get the root logger, which
# includes messages logged by all packages.
#
# The following code creates a log handler that outputs all 'ansys.grantami.bomanalytics' logger messages with severity
# INFO and above to either the terminal or the notebook.

# + tags=[]
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ansys.grantami.bomanalytics")

result = cxn.run(query)
# -
