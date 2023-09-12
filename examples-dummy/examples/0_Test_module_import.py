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

# # Test Notebook 1

# Check we can import the Connection class and instantiate some things

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url)
cxn
# -

# Also try an indicator

# + tags=[]
from ansys.grantami.bomanalytics.indicators import RoHSIndicator

indicator = RoHSIndicator(name="Indicator", legislation_ids=["Legislation"])
indicator
# -
