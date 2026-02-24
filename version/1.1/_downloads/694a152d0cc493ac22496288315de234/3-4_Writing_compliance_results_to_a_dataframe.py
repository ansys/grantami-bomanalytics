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

# # Write compliance results to a ``pandas.DataFrame`` object

# Granta MI BoM Analytics presents compliance results in a hierarchical data structure. Alternatively, you can
# represent the data in a tabular data structure, where each row contains a reference to the parent row.
# This example shows how compliance data can be translated from one format to another, making use
# of a ``pandas.DataFrame`` object to store the tabulated data.

# ## Perform a compliance query

# The first step is to perform a compliance query on an assembly that results in a deeply
# nested structure. The following code is presented without explanation. For more information, see the
# [Perform a Part Compliance Query](../2_Compliance_Queries/2-3_Part_compliance.ipynb) example.

# + tags=[]
from ansys.grantami.bomanalytics import Connection, indicators, queries

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
svhc = indicators.WatchListIndicator(
    name="SVHC",
    legislation_names=["REACH - The Candidate List"],
    default_threshold_percentage=0.1,
)
part_query = (
    queries.PartComplianceQuery()
    .with_record_history_ids([565060])
    .with_indicators([svhc])
)
part_result = cxn.run(part_query)
# -

# The ``part_result`` object contains the compliance result for every subitem. This is ideal for understanding
# compliance at a certain *level* of the structure, For example, you can display the compliance for each item directly
# under the root part.

# + tags=[]
for part in part_result.compliance_by_part_and_indicator[0].parts:
    print(
        f"Part ID: {part.record_history_identity}, "
        f"Compliance: {part.indicators['SVHC'].flag}"
    )
# -

# However, this structure makes it difficult to compare items at different levels. To do that, you want to flatten the
# data into a tabular structure.

# ## Flatten the hierarchical data structure

# You want to flatten the data into a ``list`` of ``dict`` objects, where each ``dict`` object represents an item in the
# hierarchy and each value in the ``dict`` object represents a property of this item. You can this use this structure
# can then directly or use it to construct a ``pandas.DataFrame`` object.

# First, define a helper function to transform a ``ComplianceQueryResult`` object into a ``dict`` object. In addition to
# storing properties that are intrinsic to the item (such as the ID, type, and SVHC result), you want to store
# structural information, such as the level of the item and the ID of its parent.


# + tags=[]
def create_dict(item, item_type, level, parent_id):
    """Add a BoM item to a list"""
    item_id = item.record_history_identity
    indicator = item.indicators["SVHC"]
    row = {
        "Item": item_id,
        "Parent": parent_id,
        "Type": item_type,
        "SVHC": indicator,
        "Level": level,
    }
    return row
# -

# To help with the flattening process, you also define a schema, which describes which child item types each item
# type can contain.


# + tags=[]
schema = {
    "Part": ["Part", "Specification", "Material", "Substance"],
    "Specification": ["Specification", "Coating", "Material", "Substance"],
    "Material": ["Substance"],
    "Coating": ["Substance"],
    "Substance": [],
}
# -


# The function itself performs the flattening via a stack-based approach, where the children of the item currently
# being processed are iteratively added to the ``items_to_process`` stack. Because this stack is being both modified and
# iterated over, you must use a ``while`` loop and ``.pop()`` statement instead of a ``for`` loop.

# The stack uses a special type of collection called a ``deque``, which is similar to a ``list`` but is optimized for
# these sorts of stack-type use cases involving repeated calls to ``.pop()`` and ``.extend()`` statements.


# + tags=[]
from collections import deque


def flatten_bom(root_part):
    result = []  # List to contain all dicts

    # The stack contains a deque of tuples: (item_object, item_type, level, parent_id)
    # First seed the stack with the root part
    items_to_process = deque([(root_part, "Part", 0, None)])

    while items_to_process:
        # Get the next item from the stack
        item_object, item_type, level, parent = items_to_process.pop()
        # Create the dict
        row = create_dict(item_object, item_type, level, parent)
        # Append it to the result list
        result.append(row)

        # Compute the properties for the child items
        item_id = item_object.record_history_identity
        child_items = schema[item_type]
        child_level = level + 1

        # Add the child items to the stack
        if "Part" in child_items:
            items_to_process.extend([(p, "Part", child_level, item_id)
                                     for p in item_object.parts])
        if "Specification" in child_items:
            items_to_process.extend([(s, "Specification", child_level, item_id)
                                     for s in item_object.specifications])
        if "Material" in child_items:
            items_to_process.extend([(m, "Material", child_level, item_id)
                                     for m in item_object.materials])
        if "Coating" in child_items:
            items_to_process.extend([(c, "Coating", child_level, item_id)
                                     for c in item_object.coatings])
        if "Substance" in child_items:
            items_to_process.extend([(s, "Substance", child_level, item_id)
                                     for s in item_object.substances])

    # When the stack is empty, the while loop exists. Return the result list.
    return result
# -


# Finally, call the preceding function against the results from the compliance query and use the list to create a
# ``pandas.DataFrame`` object.

# + tags=[]
import pandas as pd

data = flatten_bom(part_result.compliance_by_part_and_indicator[0])
df_full = pd.DataFrame(data)
print(f"{len(df_full)} rows")
df_full.head()
# -

# ## Postprocess the ``pandas.DataFrame`` object

# Now that you have the data in a ``pandas.DataFrame`` object, you can perform operations across all levels of the
# structure more easily. For example, you can delete all rows that are less than the 'Above Threshold' state, retaining
# only rows that are non-compliant. (Note that this reduces the number of rows significantly.)

# + tags=[]
threshold = indicators.WatchListFlag.WatchListAboveThreshold
df_non_compliant = df_full.drop(df_full[df_full.SVHC < threshold].index)
print(f"{len(df_non_compliant)} rows")
df_non_compliant.head()
# -
