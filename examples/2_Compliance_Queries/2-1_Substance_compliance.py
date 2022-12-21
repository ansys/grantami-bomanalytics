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

# # Performing a Substance Compliance Query

# A Substance Compliance Query determines whether one or more substances are compliant with the specified indicators.
# This example checks several materials for substances included on two watch lists ("REACH - The Candidate List", and
# "The SIN List 2.1"), specifying substance amounts and thresholds for compliance.

# ## Connecting to Granta MI

# Import the ``Connection`` class and create the connection. See the [Getting Started](../0_Getting_started.ipynb)
# example for more details.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Defining an Indicator

# A Compliance query determines compliance against 'Indicators', as opposed to an Impacted Substances query which
# determines compliance directly against legislations.
#
# There are two types of Indicator object (``WatchListIndicator`` and ``RohsIndicator``), and the syntax presented below
# applies to both. The differences in the internal implementation of the two objects are described in the API
# documentation.
#
# Generally speaking, if a substance is impacted by a legislation associated with an indicator, and in a quantity
# above a specified threshold, the substance is non-compliant with that indicator. This non-compliance applies to
# any other items in the BoM hierarchy that directly or indirectly include that substance.

# First, create two ``WatchListIndicator`` objects.

# + tags=[]
from ansys.grantami.bomanalytics import indicators

svhc = indicators.WatchListIndicator(
    name="SVHC",
    legislation_names=["REACH - The Candidate List"],
    default_threshold_percentage=0.1,
)
sin = indicators.WatchListIndicator(
    name="SIN",
    legislation_names=["The SIN List 2.1 (Substitute It Now!)"]
)
# -

# + [markdown] tags=[]
# ## Building and Running the Query
# -

# Next, define the query itself. Substances can be referenced by Granta MI record reference, CAS
# Number, EC Number, or Chemical Name.
#
# The substance quantity is an optional argument, and defaults to 100% if not specified.

# + tags=[]
from ansys.grantami.bomanalytics import queries

sub_query = queries.SubstanceComplianceQuery().with_indicators([svhc, sin])
sub_query = sub_query.with_cas_numbers_and_amounts([("50-00-0", 10),
                                                    ("110-00-9", 25),
                                                    ("302-17-0", 100),
                                                    ("7440-23-5", 100)])
# -

# Finally, run the query. Passing a ``SubstanceComplianceQuery`` object to the ``Connection.run()`` method returns a
# ``SubstanceComplianceQueryResult`` object.

# + tags=[]
sub_result = cxn.run(sub_query)
sub_result

# + [markdown] tags=[]
# The result object contains two properties: ``compliance_by_substance_and_indicator`` and ``compliance_by_indicator``.
# -

# ## Results Grouped by Substance

# + [markdown] tags=[]
# ``compliance_by_substance_and_indicator`` contains a list of ``SubstanceWithComplianceResult`` objects that contain
# the reference to the substance record and the compliance status in the list of indicators. To determine which
# substances are compliant, we can loop over each one and compare the indicator to a certain threshold. For this
# example, we will only examine the SVHC indicator.
# -

# The possible states of the indicator are available on the ``Indicator.available_flags`` attribute and can be compared
# using standard Python operators.

# + tags=[]
compliant_substances = []
non_compliant_substances = []
threshold = svhc.available_flags.WatchListAboveThreshold

for substance in sub_result.compliance_by_substance_and_indicator:
    if (substance.indicators["SVHC"] >= threshold):
        non_compliant_substances.append(substance)
    else:
        compliant_substances.append(substance)
# -

# Now print the SVHC and Non-SVHC substances.

# + tags=[]
compliant_cas_numbers = [sub.cas_number for sub in compliant_substances]
print(f'Non-SVHC substances: {", ".join(compliant_cas_numbers)}')

non_compliant_cas_numbers = [sub.cas_number for sub in non_compliant_substances]
print(f'SVHCs: {", ".join(non_compliant_cas_numbers)}')
# -

# ## Results Grouped by Indicator

# Alternatively, using the ``compliance_by_indicator`` property provides a single indicator result that summarizes the
# results across all substances in the query. This would be useful in a situation where we have a 'concept' material
# stored outside of Granta MI, and we want to determine its compliance. We know it contains the substances specified in
# the query above, and so using ``compliance_by_indicator`` will tell us if that concept material is compliant based on
# the worst result of the individual substances.

# + tags=[]
if sub_result.compliance_by_indicator["SVHC"] >= threshold:
    print("One or more substances is an SVHC in a quantity > 0.1%")
else:
    print("No SVHCs, or SVHCs are present in a quantity < 0.1%")
# -

# Note that this property does not tell us which substance is responsible for the non-compliance. This would require
# performing a more granular analysis as shown above, or importing the material into Granta MI and running a compliance
# query on that material record.
