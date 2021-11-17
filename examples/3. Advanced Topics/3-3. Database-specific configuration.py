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

# # Database-Specific Configuration

# ## Batch Size

# The queries that can be performed with this package are batched if they exceed a certain size. This is achieved by
# splitting the list of parts, materials, etc. into smaller lists below a certain size to reduce the overall time taken
# to perform the query. Default batch sizes have been chosen based on typical tabular attribute sizes, but under some
# situations (see the relevant page in the API documentation) these may need to be changed.

# To see the default batch size, use the batch_size property on the query.

from ansys.grantami.bomanalytics import queries
spec_query = queries.SpecificationComplianceQuery()
print(spec_query._item_argument_manager.batch_size)

# You can manually set the batch size by doing the following:

spec_query = spec_query.with_batch_size(5)
print(spec_query._item_argument_manager.batch_size)

# ## Specifying a database key

# The default database key of MI_Restricted_Substances is used by default if not specified. To specify an alternative,
# specify this on the connection object. This database key will be used for all queries made with this connection
# object.

from ansys.grantami.bomanalytics import Connection
cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
cxn.set_database_details(database_key="ACME_SUBSTANCES_DATABASE")
print(cxn._db_key)

# ## Specifying custom table names

# It is also possible to specify alternative names for the relevant Restricted Substances tables, in the case that they
# have been modified from the defaults. These are also provided to the .set_database_details() method in the same way.

cxn.set_database_details(in_house_materials_table_name="ACME Materials")
print(cxn._table_names)
