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

# # [TECHDOCS]Performing a Part Compliance Query

# A Part Compliance Query determines whether one or more parts are compliant with the specified indicators. This is
# done by first finding all substances directly or indirectly associated with that part, determining compliance for
# those substances, and then rolling up the results to the material.

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
# objects and `RohsIndicator` objects. However, the generic behavior is such that if a substance is impacted by a
# legislation that is associated with an indicator in a quantity above a threshold, the substance is non-compliant with
# that indicator. This non-compliance then rolls up the BoM hierarchy to any other items that directly or indirectly
# include that substance.

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

# Next define the query itself. Parts can be referenced by any typical Granta MI record reference or by Part Number. The
# table containing the Part records is not required, since this is enforced by the Restricted Substances database
# schema.

# + tags=[]
from ansys.grantami.bomanalytics import queries

part_query = (
    queries.PartComplianceQuery()
    .with_part_numbers(["asm_flap_mating", "DRILL"])
    .with_indicators([svhc])
)
# -

# Finally, run the query. Passing a `PartComplianceQuery` object to the `Connection.run()` method returns a
# `PartComplianceQueryResult` object.

# + tags=[]
part_result = cxn.run(part_query)
part_result

# + [markdown] tags=[]
# The result object contains two properties, `compliance_by_part_and_indicator` and `compliance_by_indicator`.
# -

# ## compliance_by_part_and_indicator

# + [markdown] tags=[]
# `compliance_by_part_and_indicator` contains a list of `PartWithComplianceResult` objects that contain the
# reference to the part record and the compliance status for each indicator. However, in Granta MI Parts can
# link to the following record types:
#
# - Parts
# - Specifications (which can link to Specifications, Materials, Substances, and Coatings)
# - Materials (which can link to Substances)
# - Substances
#
# Since compliance is determined based on the compliance of the items the record is linked to, the corresponding
# `ResultWithCompliance` objects are included in the parent `PartWithComplianceResult`, each with their own
# compliance status.
# -

# Since we specified two part records, we have received two result objects back. For this example we are only interested
# in the first one for the wing flap assembly.

# + tags=[]
wing = part_result.compliance_by_part_and_indicator[0]
print(f"Wing compliance status: {wing.indicators['SVHC'].flag.name}")
# -

# This tells us that the wing flap assembly contains an SVHC above the 0.1% threshold.

# We can print the parts below this part that also contain an SVHC above the threshold. The parts referenced by the
# 'wing' part are available in the `parts` property.

# + tags=[]
above_threshold_flag = svhc.available_flags.WatchListAboveThreshold
parts_contain_svhcs = [part for part in wing.parts
                       if part.indicators["SVHC"] >= above_threshold_flag]
print(f"{len(parts_contain_svhcs)} parts that contain SVHCs")
for part in parts_contain_svhcs:
    print(f"Part: {part.record_history_identity}")
# -

# This process can be performed recursively to show a structure of each part that contains SVHCs either directly or
# indirectly. The cells below implement the code above in a function that can be called recursively, and then call it
# on the wing flap assembly.


# + tags=[]
def recursively_print_parts_with_svhcs(parts, depth=0):
    parts_contain_svhcs = [part for part in parts
                           if part.indicators["SVHC"] >= above_threshold_flag]
    for part in parts_contain_svhcs:
        print(f"{'  '*depth}- Part: {part.record_history_identity}")
        recursively_print_parts_with_svhcs(part.parts, depth + 1)


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


# + tags=[]
def print_materials_with_svhcs(materials, depth=0):
    mats_contain_svhcs = [m for m in materials
                          if m.indicators["SVHC"] >= above_threshold_flag]
    for mat in mats_contain_svhcs:
        print(f"{'  '*depth}- Material: {mat.record_history_identity}")
        print_substances_with_svhcs(mat.substances, depth + 1)


# + tags=[]
def print_specifications_with_svhcs(specifications, depth=0):
    specs_contain_svhcs = [s for s in specifications
                           if s.indicators["SVHC"] >= above_threshold_flag]
    for spec in specs_contain_svhcs:
        print(f"{'  '*depth}- Specification: {spec.record_history_identity}")
        print_coatings_with_svhcs(spec.coatings, depth + 1)
        print_substances_with_svhcs(spec.substances, depth + 1)


# + tags=[]
def print_coatings_with_svhcs(coatings, depth=0):
    coatings_contain_svhcs = [c for c in coatings
                             if c.indicators["SVHC"] >= above_threshold_flag]
    for coating in coatings_contain_svhcs:
        print(f"{'  '*depth}- Coating: {coating.record_history_identity}")
        print_substances_with_svhcs(coating.substances, depth + 1)


# + tags=[]
def print_substances_with_svhcs(substances, depth=0):
    subs_contain_svhcs = [sub for sub in substances
                          if sub.indicators["SVHC"] >= above_threshold_flag]
    for sub in subs_contain_svhcs:
        print(f"{'  '*depth}- Substance: {sub.record_history_identity}")


# + tags=[]
recursively_print_parts_with_svhcs(wing.parts)
# -

# We have now identified the coating that is causing non-compliance. There is only one coating in the assembly that is
# non-compliant, that appears in the 4 non-compliant sub-components. Further, the coating only contains one
# non-compliant substance.

# ## compliance_by_indicator

# Alternatively, using the `compliance_by_indicator` property will give us a single indicator result that rolls up the
# results across all parts in the query. This would be useful in a situation where we have a 'concept' assembly stored
# outside of Granta MI, and we want to determine its compliance. We know it contains the sub-assemblies specified in the
# query above, and so using `compliance_by_indicator` will tell us if that concept assembly is compliant based on the
# worst result of the individual sub-assemblies.

# + tags=[]
if part_result.compliance_by_indicator["SVHC"] >= above_threshold_flag:
    print("One or more sub-assemblies contains an SVHC in a quantity > 0.1%")
else:
    print("No SVHCs, or SVHCs are present in a quantity < 0.1%")
