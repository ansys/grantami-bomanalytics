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

# # Perform a part compliance query

# A part compliance query determines whether one or more parts are compliant with the specified indicators. This is
# done by first finding all substances directly or indirectly associated with that part, determining compliance for
# those substances, and then rolling up the results to the material.

# ## Connect to Granta MI

# Import the ``Connection`` class and create the connection. For more information, see the
# [Getting Started](../0_Getting_started.ipynb) example.

# + tags=[]
from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()
# -

# ## Define an indicator

# A Compliance query determines compliance against indicators, as opposed to an Impacted Substances query which
# determines compliance directly against legislations.
#
# There are two types of indicator objects (``WatchListIndicator`` and ``RohsIndicator``), and the following syntax
# applies to both object types. The differences in the internal implementation of the two objects are described
# in the API documentation.
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

# Next define the query itself. Parts can be referenced by Granta MI record reference or part number. The
# table containing the part records is not required because this is enforced by the Restricted Substances database
# schema.

# + tags=[]
from ansys.grantami.bomanalytics import queries

part_query = (
    queries.PartComplianceQuery()
    .with_part_numbers(["asm_flap_mating", "DRILL"])
    .with_indicators([svhc])
)
# -

# Finally, run the query. Passing a ``PartComplianceQuery`` object to the ``Connection.run()`` method returns a
# ``PartComplianceQueryResult`` object.

# + tags=[]
part_result = cxn.run(part_query)
part_result
# -

# + [markdown] tags=[]
# The result object contains two properties, ``compliance_by_part_and_indicator`` and ``compliance_by_indicator``.
# -

# ## Group results by part

# + [markdown] tags=[]
# ``compliance_by_part_and_indicator`` contains a list of ``PartWithComplianceResult`` objects with the
# reference to the part record and the compliance status for each indicator.
#
# In Granta MI, parts can link to the following record types:
#
# - Parts
# - Specifications (which can link to specifications, materials, substances, and coatings)
# - Materials (which can link to substances)
# - Substances
#
# Because compliance of a part is determined based on the compliance of the items that the record is linked to, the
# corresponding ``ResultWithCompliance`` objects are included in the parent ``PartWithComplianceResult``, each with
# their own compliance status.
# -

# Because you specified two part records, you received two result objects. This example only looks in
# more detail at results for the wing flap assembly.

# + tags=[]
wing = part_result.compliance_by_part_and_indicator[0]
print(f"Wing compliance status: {wing.indicators['SVHC'].flag.name}")
# -

# This tells you that the wing flap assembly contains an SVHC above the 0.1% threshold.

# You can print the parts below this part that also contain an SVHC above the threshold. The parts referenced by the
# ``wing`` part are available in the ``parts`` property.

# + tags=[]
above_threshold_flag = svhc.available_flags.WatchListAboveThreshold
parts_contain_svhcs = [part for part in wing.parts
                       if part.indicators["SVHC"] >= above_threshold_flag]
print(f"{len(parts_contain_svhcs)} parts that contain SVHCs")
for part in parts_contain_svhcs:
    print(f"Part: {part.record_history_identity}")
# -

# This process can be performed recursively to show a structure of each part that contains SVHCs either directly or
# indirectly. The following cells implement the preceding code in a function that can be called recursively. They then
# call it on the wing flap assembly.


# + tags=[]
def recursively_print_parts_with_svhcs(parts, depth=0):
    parts_contain_svhcs = [part for part in parts
                           if part.indicators["SVHC"] >= above_threshold_flag]
    for part in parts_contain_svhcs:
        print(f"{'  '*depth}- Part: {part.record_history_identity}")
        recursively_print_parts_with_svhcs(part.parts, depth + 1)
# -


# + tags=[]
recursively_print_parts_with_svhcs(wing.parts)
# -

# This can be extended further to include all possible BoM components in the recursive iteration, including
# specifications, coatings, and substances.


# + tags=[]
def recursively_print_parts_with_svhcs(parts, depth=0):
    parts_contain_svhcs = [part for part in parts
                           if part.indicators["SVHC"] >= above_threshold_flag]
    for part in parts_contain_svhcs:
        print(f"{'  '*depth}- Part: {part.record_history_identity}")
        recursively_print_parts_with_svhcs(part.parts, depth + 1)
        print_materials_with_svhcs(part.materials, depth + 1)
        print_specifications_with_svhcs(part.specifications, depth + 1)
        print_substances_with_svhcs(part.substances, depth + 1)
# -


# + tags=[]
def print_materials_with_svhcs(materials, depth=0):
    mats_contain_svhcs = [m for m in materials
                          if m.indicators["SVHC"] >= above_threshold_flag]
    for mat in mats_contain_svhcs:
        print(f"{'  '*depth}- Material: {mat.record_history_identity}")
        print_substances_with_svhcs(mat.substances, depth + 1)
# -


# + tags=[]
def print_specifications_with_svhcs(specifications, depth=0):
    specs_contain_svhcs = [s for s in specifications
                           if s.indicators["SVHC"] >= above_threshold_flag]
    for spec in specs_contain_svhcs:
        print(f"{'  '*depth}- Specification: {spec.record_history_identity}")
        print_coatings_with_svhcs(spec.coatings, depth + 1)
        print_substances_with_svhcs(spec.substances, depth + 1)
# -


# + tags=[]
def print_coatings_with_svhcs(coatings, depth=0):
    coatings_contain_svhcs = [c for c in coatings
                             if c.indicators["SVHC"] >= above_threshold_flag]
    for coating in coatings_contain_svhcs:
        print(f"{'  '*depth}- Coating: {coating.record_history_identity}")
        print_substances_with_svhcs(coating.substances, depth + 1)
# -


# + tags=[]
def print_substances_with_svhcs(substances, depth=0):
    subs_contain_svhcs = [sub for sub in substances
                          if sub.indicators["SVHC"] >= above_threshold_flag]
    for sub in subs_contain_svhcs:
        print(f"{'  '*depth}- Substance: {sub.record_history_identity}")
# -


# + tags=[]
recursively_print_parts_with_svhcs(wing.parts)
# -

# You have now identified a coating that is causing non-compliance. While there is a single coating in
# the assembly that is non-compliant, it appears in four non-compliant subcomponents. The coating also
# only contains one non-compliant substance.

# ## Group results by indicator

# Alternatively, using the ``compliance_by_indicator`` property gives you a single indicator result that rolls up the
# results across all parts in the query. This would be useful in a situation where you have a *concept* assembly stored
# outside of Granta MI and want to determine its compliance. You know it contains the subassemblies specified in the
# preceding query, and so using ``compliance_by_indicator`` tells you if that concept assembly is compliant based on the
# worst result of the individual subassemblies.

# + tags=[]
if part_result.compliance_by_indicator["SVHC"] >= above_threshold_flag:
    print("One or more subassemblies contains an SVHC in a quantity greater than 0.1%.")
else:
    print("No SVHCs are present, or no SVHCs have a quantity less than 0.1%.")
# -
