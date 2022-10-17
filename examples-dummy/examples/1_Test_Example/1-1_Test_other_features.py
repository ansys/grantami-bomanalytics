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

# # Other Features

# ## Double-backticks

# This renders as a class: ``ansys.grantami.bomanalytics.Connection``.

# ## Hyperlinks

# This is an internal hyperlink [Parent page](../index.rst).
# This is an external hyperlink [Google](https://google.com).
# This is a link to a file [File](supporting-file.txt)

# ## Unordered list

# Here's an unordered list
#
# - Bread
# - Cheese
# - Butter

# ## Dataframes

# Here's a Pandas dataframe

# + tags=[]
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.rand(10, 10))
df.head()
# -
