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

# ## Connecting to Granta MI

# First set the log level to INFO, so we can see some key facts about the connection process.

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Then import the bom analytics module and create the connection

from ansys.grantami.bomanalytics import Connection

cxn = Connection('http://azewqami6v4/mi_servicelayer').with_autologon().build()

# ## Defining an Indicator

# In contrast to an ImpactedSubstances query, a Compliance query determines compliance against 'Indicators' as opposed
# to directly against legislations.
#
# There are two types of Indicator, which result in compliance being evaluated in similar but slightly different ways.
# In this example we will look at a Watch List indicator only, but the principles can be applied to a RoHS indicator.

from ansys.grantami.bomanalytics import indicators

svhc_indicator = indicators.WatchListIndicator(name="SVHC",
                                               legislation_names=["REACH - The Candidate List"],
                                               default_threshold_percentage=0.1)


# The cell above creates an Indicator against which compliance can be determined. The complete rules for compliance
# can be seen in the Restricted Substances documentation, but essentially if a substance appears in the queried item
# that is impacted by one of the legislations defined above, that item is non compliant.

# ## Material Compliance Query

# We can do a similar query on materials. In this case it's not relevant to specify a quantity, since the quantity of
# the substance is included in the declaration stored on the material. The overall quantity of the material is
# irrelevant, since in general the quantity of the homogeneous material does not impact the compliance of substances
# in the material.

from ansys.grantami.bomanalytics import queries
mat_query = queries.MaterialComplianceQuery().with_indicators([svhc_indicator])
mat_query = mat_query.with_material_ids(['plastic-pa66-60glassfiber', 'zinc-pb-cdlow-alloy-z21220-rolled', 'stainless-316h'])

mat_result = cxn.run(mat_query)

# A material with compliance result object contains both the compliance status for the materials, but also returns
# substance compliance results as well. This allows one to examine the source of the non-compliance.

# First print the results for the reinforced PA66 record.

pa_66 = mat_result.compliance_by_material_and_indicator[0]
print(f"PA66 (60% glass fiber): {pa_66.indicators['SVHC'].flag.name}")

# The reinforced PA66 record has the status of 'WatchListHasSubstanceAboveThreshold', which tells us the material is not
# compliant with the indicator, and therefore contains SVHCs above the 0.1% threshold.

# To understand which substances have caused this status, we can print the substances that are not compliant with the
# legislation.

above_threshold_flag = svhc_indicator.available_flags.WatchListAboveThreshold
pa_66_svhcs = [sub for sub in pa_66.substances if sub.indicators['SVHC'].flag == above_threshold_flag]
print(f"{len(pa_66_svhcs)} SVHCs")
for substance in pa_66_svhcs:
    print(f"Substance record history identity: {substance.record_history_identity}")

# Note that children of the items passed into the compliance query are returned with record references based
# on record history identities only. The Python STK can be used to translate these record history identities into CAS
# Numbers if required.

# Next we can look at the zinc alloy record.

zn_pb_cd = mat_result.compliance_by_material_and_indicator[1]
print(f"Zn-Pb-Cd low alloy: {zn_pb_cd.indicators['SVHC'].flag.name}")

# The zinc alloy record has the status 'WatchListAlloSubstancesBelowThreshold', which means there are substances present
# that are impacted by the legislation, but are below the 0.1% threshold.

# We can print these substances using the 'WatchListBelowThreshold' flag.

below_threshold_flag = svhc_indicator.available_flags.WatchListBelowThreshold
zn_svhcs_below_threshold = [sub for sub in zn_pb_cd.substances if sub.indicators['SVHC'].flag == below_threshold_flag]
print(f"{len(zn_svhcs_below_threshold)} SVHCs below threshold")
for substance in zn_svhcs_below_threshold:
    print(f"Substance record history identity: {substance.record_history_identity}")

# Finally, we can look at the stainless steel record.

ss_316h = mat_result.compliance_by_material_and_indicator[2]
print(f"316H stainless steel: {ss_316h.indicators['SVHC'].flag.name}")

# The stainless steel record has the status 'WatchListCompliant', which means there are no impacted substances at all in
# the material.

# We can print these substances using the 'WatchListNotImpacted' flag.

not_impacted_flag = svhc_indicator.available_flags.WatchListNotImpacted
ss_not_impacted = [sub for sub in ss_316h.substances if sub.indicators['SVHC'].flag == not_impacted_flag]
print(f"{len(ss_not_impacted)} non-SVHC substances")
for substance in ss_not_impacted:
    print(f"Substance record history identity: {substance.record_history_identity}")
