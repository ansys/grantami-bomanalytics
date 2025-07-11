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

# # Database-specific configuration

# Granta MI BoM Analytics work with an off-the-shelf Granta MI Restricted Substances database. However, there are
# some situations in which additional run-time configuration changes are required:
#
# - If the database key or table names have been modified from their default values, these must be set on the
#   ``Connection`` object.
# - If the number of linked records is very large, the batch sizes should be changed for each query. For more
#   information, see [Batching requests](../user_guide/batching.rst).

# ## Specify a custom database key or table name

# The default database key, ``MI_Restricted_Substances``, is used if no database key is specified. To specify a
# key, use the ``Connection.set_database_details()`` method. The specified key is then used for all queries made
# with this ``Connection`` object.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
cxn.set_database_details(database_key="ACME_SUBSTANCES_DATABASE")
cxn
# -

# It is also possible to specify alternative names for the relevant restricted substances tables if they
# have been modified from the defaults. You provide the names to the ``.set_database_details()`` method in the same way.

# + tags=[]
cxn.set_database_details(in_house_materials_table_name="ACME Materials")
cxn
# -

# ## Change batch size

# The queries that can be performed with this package are batched if they exceed a certain size. This is achieved by
# splitting the list of parts, materials, and so on into smaller lists to reduce the overall time taken
# to perform the query. Default batch sizes have been chosen based on typical tabular attribute sizes, but
# these might need to be changed in some situations. For examples, see the relevant page in the API documentation.

# The batch size is included in the query ``__repr__``. The following cell shows a ``SpecificationComplianceQuery``
# object with the default batch size.

# + tags=[]
from ansys.grantami.bomanalytics import queries

spec_query = queries.SpecificationComplianceQuery()
spec_query
# -

# You can manually set the batch size like this:

# + tags=[]
spec_query = spec_query.with_batch_size(5)
spec_query
# -

# ## Set depth of specification-to-specification links

# > Supported with Restricted Substances Reports 2023 R2 and later

# The Restricted Substances database allows Specification records to be defined in terms of other Specification records.
# Since this is a recursive relationship, there is in principle no limit to the complexity of these
# specification-to-specification (spec-to-spec) hierarchies. By default, this package considers every spec-to-spec
# hierarchy completely, with no truncation imposed.

# For typical databases this is the correct and desired behavior. However, in some circumstances, this may cause query
# times and response sizes to become very large. In such cases, you should control the maximum spec-to-spec hierarchy
# depth followed using the ``maximum_spec_link_depth`` parameter on the ``BomAnalyticsClient`` object.

# The default value is ``None``. Setting it to a positive integer limits the depth to at most that many spec-to-spec
# links.

# + tags=[]
cxn.maximum_spec_link_depth = 2
cxn
# -
