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

# # Performing a Material Compliance Query

# A Material Compliance Query determines whether one or more materials are compliant with the specified indicators. This
# is done by first determining compliance for the substances associated with the material, and then rolling up the
# results to the material.

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
    legislation_ids=["Candidate_AnnexXV"],
    default_threshold_percentage=0.1,
)
sin = indicators.WatchListIndicator(
    name="SIN",
    legislation_ids=["SINList"]
)
# -

# + [markdown] tags=[]
# ## Building and Running the Query
# -

# Next define the query itself. Materials can be referenced by Granta MI record reference or Material ID.
# The table containing the Material records is not required, since this is enforced by the Restricted Substances
# database schema.

# + tags=[]
from ansys.grantami.bomanalytics import queries

mat_query = queries.MaterialComplianceQuery().with_indicators([svhc, sin])
mat_query = mat_query.with_material_ids(["plastic-pa66-60glassfiber",
                                         "zinc-pb-cdlow-alloy-z21220-rolled",
                                         "stainless-316h"])
# -

# Finally, run the query. Passing a ``MaterialComplianceQuery`` object to the ``Connection.run()`` method returns a
# ``MaterialComplianceQueryResult`` object.

# + tags=[]
mat_result = cxn.run(mat_query)
mat_result
# -

# + [markdown] tags=[]
# The result object contains two properties: ``compliance_by_material_and_indicator`` and ``compliance_by_indicator``.
# -

# ## Results Grouped by Material

# + [markdown] tags=[]
# The ``compliance_by_material_and_indicator`` property contains a list of ``MaterialWithComplianceResult`` objects with
# the reference to the material record and the compliance status for each indicator. The
# ``SubstanceWithComplianceResult`` objects are also included because compliance was determined based on the substances
# associated with the material object. These are also accompanied by their compliance status for each indicator.
# -

# Initially, we can print just the results for the reinforced PA66 record.

# + tags=[]
pa_66 = mat_result.compliance_by_material_and_indicator[0]
print(f"PA66 (60% glass fiber): {pa_66.indicators['SVHC'].flag.name}")
# -

# The reinforced PA66 record has a status of 'WatchListHasSubstanceAboveThreshold', which tells us the material is not
# compliant with the indicator, and therefore contains SVHCs above the 0.1% threshold.

# To understand which substances have caused this status, we can print the substances that are not compliant with the
# legislation. The possible states of the indicator are available on the ``Indicator.available_flags`` attribute and
# can be compared using standard Python operators.
#
# For substances, the critical threshold is the state 'WatchListAboveThreshold'.

# + tags=[]
above_threshold_flag = svhc.available_flags.WatchListAboveThreshold
pa_66_svhcs = [sub for sub in pa_66.substances
               if sub.indicators["SVHC"] >= above_threshold_flag
               ]
print(f"{len(pa_66_svhcs)} SVHCs")
for sub in pa_66_svhcs:
    print(f"Substance record history identity: {sub.record_history_identity}")
# -

# Note that children of items passed into the compliance query are returned with record references based on record
# history identities only. The Granta MI Scripting Toolkit for Python can be used to translate record history identities
# into CAS Numbers if required.

# Next, look at the state of the zinc alloy record.

# + tags=[]
zn_pb_cd = mat_result.compliance_by_material_and_indicator[1]
print(f"Zn-Pb-Cd low alloy: {zn_pb_cd.indicators['SVHC'].flag.name}")
# -

# The zinc alloy record has the status 'WatchListAllSubstancesBelowThreshold', which means there are substances present
# that are impacted by the legislation, but are below the 0.1% threshold.

# We can print these substances using the 'WatchListBelowThreshold' flag as the threshold.

# + tags=[]
below_threshold_flag = svhc.available_flags.WatchListBelowThreshold
zn_svhcs_below_threshold = [sub for sub in zn_pb_cd.substances
                            if sub.indicators["SVHC"].flag == below_threshold_flag]
print(f"{len(zn_svhcs_below_threshold)} SVHCs below threshold")
for substance in zn_svhcs_below_threshold:
    print(
        f"Substance record history identity: {substance.record_history_identity}"
    )
# -

# Finally, look at the stainless steel record.

# + tags=[]
ss_316h = mat_result.compliance_by_material_and_indicator[2]
print(f"316H stainless steel: {ss_316h.indicators['SVHC'].flag.name}")
# -

# The stainless steel record has the status 'WatchListCompliant', which means there are no impacted substances in the
# material.

# We can print these substances using the 'WatchListNotImpacted' flag as the threshold.

# + tags=[]
not_impacted_flag = svhc.available_flags.WatchListNotImpacted
ss_not_impacted = [
    sub
    for sub in ss_316h.substances
    if sub.indicators["SVHC"].flag == not_impacted_flag
]
print(f"{len(ss_not_impacted)} non-SVHC substances")
for sub in ss_not_impacted:
    print(f"Substance record history identity: {sub.record_history_identity}")
# -

# ## Results Grouped by Indicator

# Alternatively, using the ``compliance_by_indicator`` property provides a single indicator result that summarizes the
# results across all materials in the query. This would be useful in a situation where we have a 'concept' assembly
# stored outside of Granta MI, and want to determine its compliance. We know it contains the materials specified in
# the query above, and so using ``compliance_by_indicator`` will tell us if that concept assembly is compliant based on
# the worst result from individual materials.

# + tags=[]
if mat_result.compliance_by_indicator["SVHC"] >= above_threshold_flag:
    print("One or more materials contains an SVHC in a quantity > 0.1%")
else:
    print("No SVHCs, or SVHCs are present in a quantity < 0.1%")
# -

# Note that this cannot tell us which material is responsible for the non-compliance. This would require performing a
# more granular analysis as shown above, or importing the assembly into Granta MI and running the compliance on that
# part record.
