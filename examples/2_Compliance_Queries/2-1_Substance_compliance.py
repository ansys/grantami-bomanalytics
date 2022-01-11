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

# # [TECHDOCS]Performing a Substance Compliance Query

# A Substance Compliance Query determines whether one or more substances are compliant with the specified indicators.

# ## Connecting to Granta MI

# Import the `Connection` class and create the connection. See the Getting Started example for more detail.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_service/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Defining an Indicator

# In contrast to an ImpactedSubstances query, a Compliance query determines compliance against 'Indicators' as opposed
# to directly against legislations.
#
# There are two types of Indicator, the differences between the two are described elsewhere in the documentation. The
# differences are in the internal implementation, and the interface presented here applies to both `WatchListIndicator`
# objects and `RohsIndicator` objects.
#
# Generally speaking, if a substance is impacted by a legislation that is associated with an indicator in a quantity
# above a threshold, the substance is non-compliant with that indicator. This non-compliance then rolls up the BoM
# hierarchy to any other items that directly or indirectly include that substance.

# The cell below creates two Indicators.

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


# + [markdown] tags=[]
# ## Building and Running the Query
# -

# Next define the query itself. Substances can be referenced by any typical Granta MI record reference, or by CAS
# Number, EC Number, or Chemical Name.
# The quantity of substance is optional; if not specified it will default to 100% (the worst case scenario).

# + tags=[]
from ansys.grantami.bomanalytics import queries

sub_query = queries.SubstanceComplianceQuery().with_indicators([svhc, sin])
sub_query = sub_query.with_cas_numbers_and_amounts([("50-00-0", 10),
                                                    ("110-00-9", 25),
                                                    ("302-17-0", 100),
                                                    ("7440-23-5", 100)])
# -

# Finally, run the query. Passing a `SubstanceComplianceQuery` object to the `Connection.run()` method returns a
# `SubstanceComplianceQueryResult` object.

# + tags=[]
sub_result = cxn.run(sub_query)
sub_result

# + [markdown] tags=[]
# The result object contains two properties, `compliance_by_substance_and_indicator` and `compliance_by_indicator`.
# -

# ## compliance_by_substance_and_indicator

# + [markdown] tags=[]
# `compliance_by_substance_and_indicator` contains a list of `SubstanceWithComplianceResult` objects that contain the
# reference to the substance record and the compliance status in the list of indicators. To determine which substances
# are compliant, we can loop over each one and compare the indicator to a certain threshold. For this example, we will
# only examine the SVHC indicator.
# -

# The possible states of the indicator are available on the `Indicator.available_flags` attribute, and can be compared
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

# + tags=[]
non_compliant_cas_numbers = [sub.cas_number for sub in non_compliant_substances]
print(f'SVHCs: {", ".join(non_compliant_cas_numbers)}')
# -

# ## compliance_by_indicator

# Alternatively, using the `compliance_by_indicator` property will give us a single indicator result that rolls up the
# results across all substances in the query. This would be useful in a situation where we have a 'concept' material
# stored outside of Granta MI, and we want to determine its compliance. We know it contains the substances specified in
# the query above, and so using `compliance_by_indicator` will tell us if that concept material is compliant based on
# the worst result of the individual substances.

# + tags=[]
if sub_result.compliance_by_indicator["SVHC"] >= threshold:
    print("One or more substances is an SVHC in a quantity > 0.1%")
else:
    print("No SVHCs, or SVHCs are present in a quantity < 0.1%")
# -

# Note that this cannot tell us which substance is responsible for the non-compliance. This would require performing a
# more granular analysis as shown above, or importing the material into Granta MI and running the compliance on that
# material record.
