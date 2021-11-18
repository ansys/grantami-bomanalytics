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

# # Performing a BoM Query

# Both ImpactedSubstances queries and Compliance queries can be performed on an XML Bill of Materials instead of a list
# of Granta MI records. The Bill of Materials must be in the Granta 17/11 format, and this example shows how to use the
# lxml package with the XSD XML schema file to validate the XML format.

# If the XML file is generated by a Granta MI product and has not been modified, it is possible to skip this step before
# submitting the query. However, it is strongly advised to validate the XML BoM in all situations to avoid unexpected
# server-side failures. If an invalid XML file is used in a query an exception will be raised by the `requests` HTTP
# package, but will not contain any detailed information about why the XML is non-compliant. A more detailed log will be
# reported on the Server in the MI Servicelayer log.

# ## Validating an XML file with an XSD Schema

# The `lxml` package provides a similar API to the standard library xml module, but includes some additional
# functionality, including schema validation. First import `lxml`, and then build a simple validator function that takes
# the xml file and schema file, and returns the result.

# + tags=[]
from lxml import etree


def xml_validator(xml: str, schema_file: str) -> bool:
    schema = etree.XMLSchema(file=schema_file)
    doc = etree.fromstring(xml)
    return schema.validate(doc)


# -

# We can now use this function to test the validity of a BoM generated by the BoM Analyzer.

# + tags=[]
valid_xml_file = "../supporting-files/bom-complex.xml"
with open(valid_xml_file) as f:
    valid_xml = f.read()
result = xml_validator(valid_xml, "../supporting-files/BillOfMaterialsEco.xsd")
result
# -

# We can also test a BoM which is valid XML, but is non-compliant with the schema.

# + tags=[]
invalid_xml_file = "../supporting-files/invalid-bom.xml"
with open(invalid_xml_file) as f:
    invalid_xml = f.read()
result = xml_validator(invalid_xml, "../supporting-files/BillOfMaterialsEco.xsd")
result
# -

# ## Running an XML-based Query

# Now we have validated the XML, we can build our XML BoM-based query.

# Set logging to INFO to eliminate some noise from the log entries.

# + tags=[]
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# + tags=[]
from ansys.grantami.bomanalytics import Connection
cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
# -

# ### BomImpactedSubstancesQuery

# The Impacted Substances BoM query behaves similar to other Impacted Substances queries. However, a BoM query can only
# accept a single BoM at a time, and so we only ever receive a single list of substances impacted by the specified
# legislations.

# + tags=[]
from ansys.grantami.bomanalytics import queries
SIN_LIST = 'The SIN List 2.1 (Substitute It Now!)'
is_query = queries.BomImpactedSubstancesQuery().with_bom(valid_xml).with_legislations([SIN_LIST])

# + tags=[]
is_query_result = cxn.run(is_query)
is_query_result
# -

# The `BomImpactedSubstancesQueryResult` object returned after running the ImpactedSubsances query now behaves similarly
# to any other Impacted Substances result object. For example, we can print all subtances impacted by the legislation
# using an approach from a previous example.

# + tags=[]
from tabulate import tabulate
rows = [[substance.cas_number, substance.max_percentage_amount_in_material]
        for substance in is_query_result.impacted_substances]
print(f'Substances impacted by "{SIN_LIST}" in a BoM (first 10 only, {len(rows)} total)')
print(tabulate(rows[:10], headers=['CAS Number', 'Amount (wt. %)']))
# -

# #### BomComplianceQuery

# Running a BoM Compliance Query produces the same result as if we had stored the Bom structure as linked 'Products and
# Parts' records in Granta MI.

# + tags=[]
from ansys.grantami.bomanalytics import indicators
svhc_indicator = indicators.WatchListIndicator(name="SVHC",
                                               legislation_names=["REACH - The Candidate List"],
                                               default_threshold_percentage=0.1)
c_query = queries.BomComplianceQuery().with_bom(valid_xml).with_indicators([svhc_indicator])

# + tags=[]
c_query_result = cxn.run(c_query)
c_query_result
# -

# The `BomComplianceQueryResult` object returned after running the Compliance query contains a list of
# `PartWithComplianceResult` objects, the behavior of which has been covered in a previous example. The cell below shows
# printing the compliance status of the BoM.

# + tags=[]
root_part = c_query_result.compliance_by_part_and_indicator[0]
print(f"BoM Compliance Status: {root_part.indicators['SVHC'].flag.name}")
# -

# #### Invalid BoM Exception

# If we were to try the same query with the invalid BoM, we would see a stack trace informing us that MI Servicelayer
# responded with a 500 HTTP response code. Change the constant below to True to raise the exception.

# + tags=[]
broken_query = queries.BomImpactedSubstancesQuery().with_bom(invalid_xml).with_legislations([SIN_LIST])

RUN_QUERY = False

if RUN_QUERY:
    cxn.run(broken_query)
