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

# # [TECHDOCS]Database-Specific Configuration Options

# The BoM Analytics package will work with an off-the-shelf Granta MI Restricted Substances database. However, there are
# some situations in which additional run-time configuration changes are required:
#
# - If the database key or table names have been modified from their default values, these must be set on the
#   `Connection` object
# - If the number of linked records is very large, the batch sizes should be changed for each query (see xxxx for more
#   details)

# ## Specifying a Custom Database Key or Table Name

# The default database key of MI_Restricted_Substances is used by default if not specified. To specify an alternative,
# use the `Connection.set_database_details()` method. This database key will be used for all queries made with this
# `Connection` object.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_service/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
cxn.set_database_details(database_key="ACME_SUBSTANCES_DATABASE")
cxn
# -

# It is also possible to specify alternative names for the relevant Restricted Substances tables, in the case that they
# have been modified from the defaults. These are also provided to the .set_database_details() method in the same way.

cxn.set_database_details(in_house_materials_table_name="ACME Materials")
cxn

# ## Batch Size

# The queries that can be performed with this package are batched if they exceed a certain size. This is achieved by
# splitting the list of parts, materials, etc. into smaller lists below a certain size to reduce the overall time taken
# to perform the query. Default batch sizes have been chosen based on typical tabular attribute sizes, but under some
# situations (see the relevant page in the API documentation) these may need to be changed.

# To see the default batch size, use the batch_size property on the query.

from ansys.grantami.bomanalytics import queries

spec_query = queries.SpecificationComplianceQuery()
spec_query

# You can manually set the batch size by doing the following:

# + tags=[]
spec_query = spec_query.with_batch_size(5)
spec_query
