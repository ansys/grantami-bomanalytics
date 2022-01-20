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

# # [TECHDOCS]Getting Started

# ## Introduction

# This example describes how to connect to Granta MI and perform a basic Impacted Substances query. It also describes
# how to view logging messages returned by the Granta MI server. It does not go into detail about the results of the
# queries, please see the other examples for further detail in this area.

# ## Connect to Granta MI

# The first step is to connect to the Granta MI server. Use the `ansys.grantami.bomanalytics.Connection` class to create
# a connection. The `Connection` class uses a fluent interface to build the connection which is always invoked in the
# following sequence:
#
# 1. Specify the Granta MI Service Layer URL as a parameter to the `Connection` class
# 2. Specify the authentication method using one of the `Connection.with_...()` methods
# 3. Use the `Connection.connect()` method to finalize the connection. This returns a connection object which is called
#    `cxn` in these examples.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
# -

# If the Python script is running on Windows, in most cases you will be able to use the `.with_autologon()`.

# + tags=[]
cxn = Connection(server_url).with_autologon().connect()
cxn
# -

# If the Python script is running on Linux without Kerberos enabled, or you wish to use an account other than your
# logged-in account, you can specify credentials explicitly.

# + tags=[]
cxn = Connection(server_url).with_credentials("my_username", "my_password").connect()
cxn
# -

# OIDC and anonymous authentication methods are also available, but these are beyond the scope of this example. See
# the documentation for the `ansys-openapi-common` package for more details.

# ## Construct a Query

# Queries are also constructed using a fluent interface. However, the `Query` constructor takes no arguments; all the
# details of the query are specified on `Query` methods.  To demonstrate this, we will aim to build a query that
# determines the substances present in an ABS material that are impacted by the REACH Candidate List legislation.

# First import the `queries` module and create a `MaterialImpactedSubstancesQuery` object.

# + tags=[]
from ansys.grantami.bomanalytics import queries

query = queries.MaterialImpactedSubstancesQuery()
query
# -

# Now add the material that we wish to query by specifying its material ID. Note: other methods of specifying records
# are available; these are discussed in other examples.

# + tags=[]
query = query.with_material_ids(["plastic-abs-high-impact"])
query
# -

# Note that because the `MaterialImpactedSubstancesQuery` object has a fluent interface, we receive the same object back
# that we started with, just with the Material IDs added. Finally, add the legislation to the query.

# + tags=[]
query = query.with_legislations(["REACH - The Candidate List"])
query
# -

# However, fluent interfaces are intended to allow a complex object to be constructed in a single line of code. We can
# consolidate the above cells to create the object in a single step:

# + tags=[]
query = queries.MaterialImpactedSubstancesQuery().with_material_ids(["plastic-abs-high-impact"]).with_legislations(["REACH - The Candidate List"])  # noqa: E501
query
# -

# Since the fluent interface can produce very long lines of code, it is required to break the query creation into
# multiple lines. The following multi-line format is used throughout the examples, and is functionally equivalent to
# the cell above.

# + tags=[]
query = (
    queries.MaterialImpactedSubstancesQuery()
    .with_material_ids(["plastic-abs-high-impact"])
    .with_legislations(["REACH - The Candidate List"])
)
query
# -

# The cell above is the recommended way of creating queries using this API.

# ## Run a Query

# Now we have our `cxn` and `query` objects, we can use the `cxn.run()` method to run the query. This returns an object
# that contains the results of the query.

# + tags=[]
result = cxn.run(query)
result
# -

# ## Query Results

# In the case of an `MaterialsImpactedSubstancesQuery`, the results object contains the list of substances present in
# the material that are impacted by the specified legislations.

# + tags=[]
result.impacted_substances
# -

# ## Logging

# All query results contain a list of messages that were returned by the server when running the query. These are
# sorted in order of decreasing severity. The same messages are also available in the Service Layer log file.

# + tags=[]
result.messages
# -

# These messages are also available via the standard `logging` module using the 'ansys.grantami.bomanalytics' logger.
# Alternatively, omit the logger name to get the root logger, which will include messages logged by all packages.
# The code below creates a log handler that outputs all bomanalytics messages with severity INFO and above to either the
# terminal or the notebook.

# + tags=[]
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ansys.grantami.bomanalytics")

result = cxn.run(query)
# -
