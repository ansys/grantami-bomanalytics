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

# # Database-Specific Configuration Options

# The BoM Analytics package will work with an off-the-shelf Granta MI Restricted Substances database. However, there are
# some situations in which additional run-time configuration changes are required:
#
# - If the database key or table names have been modified from their default values, these must be set on the
#   ``Connection`` object
# - If the number of linked records is very large, the batch sizes should be changed for each query (see
#   [Batching Requests](../../api/batching.rst) for more details)

# ## Specifying a Custom Database Key or Table Name

# The default database key, ``MI_Restricted_Substances``, is used if no database key is specified. To specify an
# alternative, use the ``Connection.set_database_details()`` method. This database key will be used for all queries made
# with this ``Connection`` object.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
cxn.set_database_details(database_key="ACME_SUBSTANCES_DATABASE")
cxn
# -

# It is also possible to specify alternative names for the relevant Restricted Substances tables, if they
# have been modified from the defaults. These are provided to the ``.set_database_details()`` method in the same way.

# + tags=[]
cxn.set_database_details(in_house_materials_table_name="ACME Materials")
cxn
# -

# ## Batch Size

# The queries that can be performed with this package are batched if they exceed a certain size. This is achieved by
# splitting the list of parts, materials, etc. into smaller lists to reduce the overall time taken
# to perform the query. Default batch sizes have been chosen based on typical tabular attribute sizes, but
# these may need to be changed in some situations (see the relevant page in the API documentation for examples).

# The batch size is included in the query ``__repr__``. The cell below shows a ``SpecificationComplianceQuery`` object
# with the default batch size.

# + tags=[]
from ansys.grantami.bomanalytics import queries

spec_query = queries.SpecificationComplianceQuery()
spec_query
# -

# You can manually set the batch size by doing the following:

# + tags=[]
spec_query = spec_query.with_batch_size(5)
spec_query
# -
