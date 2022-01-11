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

# # [TECHDOCS]Writing Compliance Results to a DataFrame

# ## Introduction

# The BoM Analytics package presents compliance results in a hierarchical data structure. An alternative way of
# representing the data is in a tabular data structure, where each row contains a reference to the parent row.
# This example shows an example of how the data could be translated from one format to another, and makes use
# of a `pandas.DataFrame` object to store the tabulated data.

# ## Perform a Compliance Query

# The first step is to perform a compliance query on an assembly that will result in a deeply
# nested structure. The code here is presented without explanation, see other examples for more
# detail.

# + tags=[]
from ansys.grantami.bomanalytics import Connection, indicators, queries

server_url = "http://my_grantami_service/mi_servicelayer"
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

# The `part_result` object contains the compliance result for every sub-item. This is ideal for understanding
# compliance at a certain 'level' of the structure, e.g. we can display the compliance for each item directly
# under the root part.

for part in part_result.compliance_by_part_and_indicator[0].parts:
    print(
        f"Part ID: {part.record_history_identity}, "
        f"Compliance: {part.indicators['SVHC'].flag}"
    )

# However, it is less useful to be able to compare items at different levels. For this, we can flatten the data into a
# tabular structure.

# ## Flatten the Hierarchical Data Structure

# We will flatten the data into a `list` of `dict` objects, where each `dict` represents an 'item' in the
# hierarchy, and each value in the `dict` represents a property of that item. This structure can then either
# be used directly or can be used to construct a `DataFrame`.

# First define a helper function that will transform a ComplianceResult object into a dict. In addition to storing
# properties that are intrinsic to the item (e.g. the ID, the type, and the SVHC result), we also want to store
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

# To help with the flattening process, we will also define a schema, which describes for each item type what
# child item types it can contain.


schema = {
    "Part": ["Part", "Specification", "Material", "Substance"],
    "Specification": ["Specification", "Coating", "Material", "Substance"],
    "Material": ["Substance"],
    "Coating": ["Substance"],
    "Substance": [],
}


# The function itself performs the flattening via a stack-based approach, by which the children of the item currently
# being processed are iteratively added to the `items_to_process` stack. Since this stack is both being moderated and
# iterated over, we must use a while loop and a .pop() statement instead of a for loop.

# The stack uses a special type of collection called a `deque`, which is similar to a `list` but is optimized for
# these sorts of stack-type use cases which involve repeated calls to .pop() and .extend().


# + tags=[]
from collections import deque


def flatten_bom(root_part):
    result = []  # List that will contain all dicts

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

# Finally, call the function above against the results from the compliance query, and use the list to create a
# `DataFrame`.

# + tags=[]
import pandas as pd

data = flatten_bom(part_result.compliance_by_part_and_indicator[0])
df_full = pd.DataFrame(data)
print(f"{len(df_full)} rows")
df_full.head()
# -

# ## Post-processing the DataFrame

# Now we have the data in a `DataFrame` we can perform operations across all levels of the structure more easily.
# For example, we can delete all rows that are less than the 'Above Threshold' state, retaining only rows that are
# non-compliant. Note that this reduces the number of rows significantly.

# + tags=[]
threshold = indicators.WatchListFlag.WatchListAboveThreshold
df_non_compliant = df_full.drop(df_full[df_full.SVHC < threshold].index)
print(f"{len(df_non_compliant)} rows")
df_non_compliant.head()
