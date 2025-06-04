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

# # Perform a substance compliance query

# A substance compliance query determines whether one or more substances are compliant with the specified indicators.
# This example checks several materials for substances included on two watch lists ("EU REACH - The Candidate List" and
# "The SIN List 2.1"), specifying substance amounts and thresholds for compliance.

# ## Connect to Granta MI

# Import the ``Connection`` class and create the connection. For more information, see the
# [Basic Usage](../0_Basic_usage.ipynb) example.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Define an indicator

# A Compliance query determines compliance against indicators, as opposed to an Impacted Substances query which
# determines compliance directly against legislations.
#
# There are two types of indicator objects (``WatchListIndicator`` and ``RohsIndicator``), and the syntax that
# follows applies to both object types. The differences in the internal implementation of the two objects are
# described in the API documentation.
#
# Generally speaking, if a substance is impacted by a legislation associated with an indicator and in a quantity
# above a specified threshold, the substance is non-compliant with that indicator. This non-compliance applies to
# any other items in the BoM hierarchy that directly or indirectly include that substance.

# First, create two ``WatchListIndicator`` objects.

# + tags=[]
from ansys.grantami.bomanalytics import indicators

svhc = indicators.WatchListIndicator(
    name="SVHC",
    legislation_ids=["Candidate_AnnexXV"],
    default_threshold_percentage=0.1,
)
sin = indicators.WatchListIndicator(
    name="SIN",
    legislation_ids=["SINList"]
)
# -

# + [markdown] tags=[]
# ## Build and run the query
# -

# Next, define the query itself. Substances can be referenced by Granta MI record reference, CAS
# number, EC number, or chemical name.
#
# The substance quantity, an optional argument, defaults to 100% if no value is specified.

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

# ## Group results by substance

# + [markdown] tags=[]
# ``compliance_by_substance_and_indicator`` contains a list of ``SubstanceWithComplianceResult`` objects that contain
# the reference to the substance record and the compliance status in the list of indicators. To determine which
# substances are compliant, loop over each one and compare the indicator to a certain threshold. This
# example examines the SVHC indicator.
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

# Now print the SVHC and non-SVHC substances.

# + tags=[]
compliant_cas_numbers = [sub.cas_number for sub in compliant_substances]
print(f'Non-SVHC substances: {", ".join(compliant_cas_numbers)}')

non_compliant_cas_numbers = [sub.cas_number for sub in non_compliant_substances]
print(f'SVHCs: {", ".join(non_compliant_cas_numbers)}')
# -

# ## Group results by indicator

# Alternatively, using the ``compliance_by_indicator`` property provides a single indicator result
# that summarizes the results across all substances in the query. This would be useful in a situation
# where a *concept* material is stored outside of Granta MI but its compliance must be determined.
# Because you know it contains the substances specified in the preceding query, you can use the
# ``compliance_by_indicator`` property to tell if this concept material is compliant based on
# the worst result of the individual substances.

# + tags=[]
if sub_result.compliance_by_indicator["SVHC"] >= threshold:
    print("One or more substances is an SVHC with a quantity greater than 0.1%")
else:
    print("No SVHCs are present, or no SVHCs have a quantity less than 0.1%.")
# -

# Note that this property does not tell you which substance is responsible for the non-compliance. This would require
# either performing a more granular analysis as shown earlier or importing the material into Granta MI and running
# a compliance query on that material record.
