# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # BoM sustainability summary: messages and phase summary
#
# The following supporting files are required for this example:
#
# * [sustainability-bom-2412.xml](supporting-files/sustainability-bom-2412.xml)

# <div class="alert alert-info">
#
# **Info:**
#
# This example uses an input file that is in the 24/12 XML BoM format. This structure requires Granta MI Restricted
# Substances and Sustainability Reports 2025 R2 or later.
#
# To run this example with an older version of the reports bundle, use
# [sustainability-bom-2301.xml](supporting-files/sustainability-bom-2301.xml) instead. Some sections of this example
# will produce different results from the published example when this BoM is used.
# </div>

# + [markdown] jp-MarkdownHeadingCollapsed=true
# ## Example scope
#
# This example only shows the ``messages`` and ``phases_summary`` properties. For other properties, see the other
# examples in this section:
#
# * BoM sustainability summary: transport
#   * ``transport_details``
#   * ``distribution_transport_summary``
#   * ``manufacturing_transport_summary``
#   * ``transport_details_aggregated_by_part``
# * BoM sustainability summary: material
#   * ``material_details``
# * BoM sustainability summary: processes
#   * ``primary_processes_details``
#   * ``secondary_processes_details``
#   * ``joining_and_finishing_processes_details``
#
# The "BoM sustainability summary: hierarchical plots" summarizes all the processed data into plots which represent
# the hierarchy of the data.
# -

# ## Run a BoM sustainability summary query
#
# First, connect to Granta MI.
#

# +
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# Next, create a sustainability summary query. The query accepts a single BoM as argument and an optional
# configuration for units. If a unit is not specified, the default unit is used. Default units for the analysis are
# ``MJ`` for energy, ``kg`` for mass, and ``km`` for distance.

# +
xml_file_path = "supporting-files/sustainability-bom-2412.xml"
with open(xml_file_path) as f:
    bom = f.read()

from ansys.grantami.bomanalytics import queries

MASS_UNIT = "kg"
ENERGY_UNIT = "MJ"
DISTANCE_UNIT = "km"

sustainability_summary_query = (
    queries.BomSustainabilitySummaryQuery()
    .with_bom(bom)
    .with_units(mass=MASS_UNIT, energy=ENERGY_UNIT, distance=DISTANCE_UNIT)
)
# -

sustainability_summary = cxn.run(sustainability_summary_query)
sustainability_summary

# ## Messages
#
# The ``BomSustainabilitySummaryQueryResult`` object that is returned implements a ``messages`` property and properties
# showing the environmental impact of the items included in the BoM.
# Log messages are sorted by decreasing severity. The same messages are available in the MI Service Layer log file
# and are logged using the standard ``logging`` module.
#
# If there are no messages, an empty list is returned. This means there were no unexpected events during BoM analysis.

sustainability_summary.messages

# ## Phases summary
#
# The ``phases_summary`` property summarizes the environmental impact contributions by lifecycle phase: materials,
# processes, and transport phases. The results for each phase include their absolute and relative contributions to
# the product as a whole.

sustainability_summary.phases_summary

# Use the [pandas](https://pandas.pydata.org/) and [plotly](https://plotly.com/python/) libraries to visualize the
# results. First, the data is translated from the BoM Analytics ``BomSustainabilitySummaryQueryResult`` to a pandas
# ``Dataframe`` object.

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"

phases_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.name,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.phases_summary
    ]
)
phases_df
# -

# Next, the dataframe is visualized as a pair of pie charts.

# +
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Embodied Energy", "Climate Change"],
    )
fig.add_trace(go.Pie(labels=phases_df["Name"], values=phases_df[EE_HEADER], name=ENERGY_UNIT), 1, 1)
fig.add_trace(go.Pie(labels=phases_df["Name"], values=phases_df[CC_HEADER], name=MASS_UNIT), 1, 2)
fig.update_layout(title_text="BoM sustainability summary - By phase", legend=dict(orientation="h"))
fig.update_traces(textposition="inside", textinfo="percent+label", hoverinfo="value+name")
fig.show()
