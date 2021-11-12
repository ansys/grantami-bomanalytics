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

# # Performing a Compliance Query

# Compliance queries are typically used to determine the overall compliance of a material, specification, part, or Bill
# of Materials against one or more legislations, without necessarily caring specifically which substances are causing
# the lack of compliance (although this information is still available).

# This example will go through how to run a compliance query against different items and how to interpret the results.

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

# ## Substance compliance query

# The simplest compliance query is a Substance Compliance Query. This takes one or more substances and one or more
# indicators, and determines for each substance whether it is compliant with the provided indicators.
#
# Substances can be referenced by any typical Granta MI record reference, or by CAS Number, EC Number, or Chemical Name.
# The quantity of substance is optional; if not specified it will default to 100% (the worst case scenario).

from ansys.grantami.bomanalytics import queries

sub_query = queries.SubstanceComplianceQuery().with_indicators([svhc_indicator])
sub_query = sub_query.with_cas_numbers_and_amounts([('50-00-0', 10),
                                                    ('110-00-9', 25),
                                                    ('302-17-0', 100),
                                                    ('7440-23-5', 100)])

# Now run the query against the database using the connection from above

sub_result = cxn.run(sub_query)
sub_result

# The result object contains two properties, `compliance_by_substance_and_indicator` and `compliance_by_indicator`.
#
# `compliance_by_substance_and_indicator` is a list of `SubstanceWithComplianceResult` objects that contain the
# reference to the substance record and the compliance status in the list of indicators. To determine which substances
# are compliant, we can loop over each one and compare the indicator to a certain threshold.

compliant_substances = []
non_compliant_substances = []
for substance in sub_result.compliance_by_substance_and_indicator:
    if substance.indicators['SVHC'].flag in [svhc_indicator.available_flags.WatchListHasSubstanceAboveThreshold,
                                             svhc_indicator.available_flags.WatchListAboveThreshold]:
        non_compliant_substances.append(substance)
    else:
        compliant_substances.append(substance)

compliant_cas_numbers = ", ".join([sub.cas_number for sub in compliant_substances])
print(f"Compliant substances: {compliant_cas_numbers}")

non_compliant_cas_numbers = ", ".join([sub.cas_number for sub in non_compliant_substances])
print(f"SVHCs: {non_compliant_cas_numbers}")
