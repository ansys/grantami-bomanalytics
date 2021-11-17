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

# # Writing Compliance Results to a DataFrame

# ## Introduction

# This example provides an example method of translating the the hierarchical compliance results into a flat data
# structure such as a DataFrame.

## Perform a Compliance Query

# See a previous example for more detail on compliance queries.

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from ansys.grantami.bomanalytics import Connection, indicators, queries

cxn = Connection('http://localhost/mi_servicelayer').with_autologon().build()
svhc_indicator = indicators.WatchListIndicator(name="SVHC",
                                               legislation_names=["REACH - The Candidate List"],
                                               default_threshold_percentage=0.1)
part_query = queries.PartComplianceQuery().with_record_history_ids([565060]).with_indicators([svhc_indicator])
part_result = cxn.run(part_query)

# ## Load the Results into a DataFrame

# The following cells describe how to flatten the hierarchical data structure into a format that can be used to create
# a DataFrame.

# First define a helper function that will return a dictionary that will represent a row in our dataframe. Each key
# is the name of a column, with the corresponding value being the value in that cell.


def append_item(level: int, item_type: str, item, parent):
    """Add a BoM item to a list"""
    item_id = item.record_history_identity
    row = {"Item": item_id,
           "Parent": parent,
           "Type": item_type,
           "SVHC": item.indicators["SVHC"],
           "Level": level}
    return row


# Next define the function that will do the actual flattening of the data structure. Since we will need to switch
# based on the type of the result, we need to perform some imports from a private module in Bom Analytics. This is
# generally discouraged, but in this case is the most pragmatic way to achieve this functionality.

# Note that since these imports are from a private module, they are more likely to change than types from a public
# module.


from ansys.grantami.bomanalytics._item_results import (
    PartWithComplianceResult as PartResult,
    MaterialWithComplianceResult as MaterialResult,
    SpecificationWithComplianceResult as SpecResult,
    CoatingWithComplianceResult as CoatingResult,
    SubstanceWithComplianceResult as SubstanceResult,
)


# The function itself takes a collection of items which is appended to from within the loop, hence the use of a while
# loop and a .pop() statement instead of a for loop. Each item is added to a list, and then the child items are
# added to the collection. In this way, each item in the hierarchical structure is flattened into a tabular structure.

# This function uses a special type of collection called a `deque`, which is similar to a list but is optimized for
# these sorts of stack-type use cases which involve frequent calls to .pop() and .extend().

from collections import deque


def process_bom(part):
    data = []
    items_to_process = deque([(0, None, part)])

    while items_to_process:
        level, parent, item = items_to_process.pop()
        item_id = item.record_history_identity
        if isinstance(item, PartResult):
            row = append_item(level, "Part", item, parent)
            items_to_process.extend([(level+1, item_id, p) for p in item.parts])
            items_to_process.extend([(level+1, item_id, s) for s in item.specifications])
            items_to_process.extend([(level+1, item_id, m) for m in item.materials])
            items_to_process.extend([(level+1, item_id, s) for s in item.substances])
        elif isinstance(item, SpecResult):
            row = append_item(level, "Specification", item, parent)
            items_to_process.extend([(level+1, item_id, s) for s in item.specifications])
            items_to_process.extend([(level+1, item_id, c) for c in item.coatings])
            items_to_process.extend([(level+1, item_id, m) for m in item.materials])
            items_to_process.extend([(level+1, item_id, s) for s in item.substances])
        elif isinstance(item, CoatingResult):
            row = append_item(level, "Coating", item, parent)
            items_to_process.extend([(level+1, item_id, s) for s in item.substances])
        elif isinstance(item, MaterialResult):
            row = append_item(level, "Material", item, parent)
            items_to_process.extend([(level+1, item_id, s) for s in item.substances])
        elif isinstance(item, SubstanceResult):
            row = append_item(level, "Substance", item, parent)
        else:
            raise NotImplementedError
        data.append(row)
    return data

# Finally, call the function above against the results from the compliance query, and use to create a DataFrame.

import pandas as pd
data = process_bom(part_result.compliance_by_part_and_indicator[0])
df = pd.DataFrame(data)
print(f"{len(df)} rows")
df.head()

# ## Post-processing the DataFrame

# Now we have the data 'flattened' into a DataFrame, we can perform operations in bulk more easily. For example, we can
# delete all rows who's indicator is below a certain threshold.

# In this example we delete all rows that are less than the 'Above Threshold' state. This means we will retain any
# rows that are non-compliant. Not that the number of rows has decreased significantly.

threshold = indicators.WatchListFlag.WatchListAboveThreshold
df_non_compliant = df.drop(df[df.SVHC < threshold].index)
print(f"{len(df_non_compliant)} rows")
df_non_compliant.head()

# We can also extract the name of the indicator from the object, leaning to a more typical dataframe structure. Note
# that the number of rows is unchanged after this operation.

df_non_compliant['SVHC'] = df_non_compliant['SVHC'].apply(lambda x: x.flag.name)
print(f"{len(df_non_compliant)} rows")
df_non_compliant.head()
