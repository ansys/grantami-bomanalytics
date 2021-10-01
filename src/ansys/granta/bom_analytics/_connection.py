from typing import overload, TYPE_CHECKING
from ansys.granta import bomanalytics, auth_common

if TYPE_CHECKING:
    from ansys.granta.bom_analytics.queries import (
        MaterialImpactedSubstances,
        MaterialCompliance,
        PartImpactedSubstances,
        PartCompliance,
        SpecificationImpactedSubstances,
        SpecificationCompliance,
        SubstanceCompliance,
        BomImpactedSubstances,
        BomCompliance,
    )
    from ansys.granta.bom_analytics._query_results import (
        MaterialImpactedSubstancesResult,
        MaterialComplianceResult,
        PartImpactedSubstancesResult,
        PartComplianceResult,
        SpecificationImpactedSubstancesResult,
        SpecificationComplianceResult,
        SubstanceComplianceResult,
        BomImpactedSubstancesResult,
        BomComplianceResult,
    )


class BomServicesClient(auth_common.ApiClient):
    @overload
    def run(self, query: "MaterialImpactedSubstances") -> "MaterialImpactedSubstancesResult":
        ...

    @overload
    def run(self, query: "MaterialCompliance") -> "MaterialComplianceResult":
        ...

    @overload
    def run(self, query: "PartImpactedSubstances") -> "PartImpactedSubstancesResult":
        ...

    @overload
    def run(self, query: "PartCompliance") -> "PartComplianceResult":
        ...

    @overload
    def run(self, query: "SpecificationImpactedSubstances") -> "SpecificationImpactedSubstancesResult":
        ...

    @overload
    def run(self, query: "SpecificationCompliance") -> "SpecificationComplianceResult":
        ...

    @overload
    def run(self, query: "SubstanceCompliance") -> "SubstanceComplianceResult":
        ...

    @overload
    def run(self, query: "BomImpactedSubstances") -> "BomImpactedSubstancesResult":
        ...

    @overload
    def run(self, query: "BomCompliance") -> "BomComplianceResult":
        ...

    def run(self, query):
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        query : Query
            A compliance or impacted substance query

        Returns
        -------
        Result
            The corresponding result object based on the provided query
        """

        api = query.api(self)
        api_method = getattr(api, query.api_method)
        return query.run_query(api_method)


class Connection(auth_common.ApiClientFactory):
    """
    Build a connection to an instance of Granta MI.

    Parameters
    ----------
    servicelayer_url : str
        The url to the Granta MI service layer

    Examples
    --------
    >>> conn = Connection(servicelayer_url="http://my_mi_server/mi_servicelayer").with_autologon().build()

    >>> conn = Connection(servicelayer_url="http://my_mi_server/mi_servicelayer") \
    ...     .with_credentials(username="my_username", password="my_password") \
    ...     .build()
    """

    def build(self) -> BomServicesClient:
        self._validate_builder()
        client = BomServicesClient(self._session, self._sl_url, self._session_configuration)
        client.setup_client(bomanalytics.models)
        return client
