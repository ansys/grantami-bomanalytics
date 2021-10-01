from typing import overload, TYPE_CHECKING, Union
from ansys.granta import bomanalytics, auth_common

DEFAULT_DBKEY = "MI_Restricted_Substances"

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_key = DEFAULT_DBKEY
        self._material_universe_table_name: Union[str, None] = None
        self._in_house_materials_table_name: Union[str, None] = None
        self._specifications_table_name: Union[str, None] = None
        self._products_and_parts_table_name: Union[str, None] = None
        self._substances_table_name: Union[str, None] = None
        self._coatings_table_name: Union[str, None] = None

    def set_database_details(
        self,
        database_key: str = DEFAULT_DBKEY,
        material_universe_table_name: Union[str, None] = None,
        in_house_materials_table_name: Union[str, None] = None,
        specifications_table_name: Union[str, None] = None,
        products_and_parts_table_name: Union[str, None] = None,
        substances_table_name: Union[str, None] = None,
        coatings_table_name: Union[str, None] = None,
    ):
        """
        Configure the database key and table names if the defaults in Granta MI have been modified.

        The database key is required if something other than MI_Restricted_Substances is being used. Table names are
        required if they have been modified from the defaults.

        Parameters
        ----------
        database_key : str, default="MI_Restricted_Substances"
            As-implemented database key of the Restricted Substances-based database.
        material_universe_table_name : str, optional
            As-implemented name for the 'MaterialUniverse' table
        in_house_materials_table_name : str, optional
            As-implemented name for the 'Materials - in house' table
        specifications_table_name : str, optional
            As-implemented name for the 'Specifications' table
        products_and_parts_table_name : str, optional
            As-implemented name for the 'Products and parts' table
        substances_table_name : str, optional
            As-implemented name for the 'Restricted Substances' table
        coatings_table_name : str, optional
            As-implemented name for the 'Coatings' table

        Examples
        --------
        >>> conn = Connection(...)
        >>> conn.set_database_details(database_key = "ACME_RS",
        ...                           in_house_materials_table_name = "ACME Materials")
        """

        self._db_key = database_key
        self._material_universe_table_name = material_universe_table_name
        self._in_house_materials_table_name = in_house_materials_table_name
        self._specifications_table_name = specifications_table_name
        self._products_and_parts_table_name = products_and_parts_table_name
        self._substances_table_name = substances_table_name
        self._coatings_table_name = coatings_table_name

    @property
    def _query_config(self) -> Union[bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig, None]:
        if (
            self._material_universe_table_name
            or self._in_house_materials_table_name
            or self._specifications_table_name
            or self._products_and_parts_table_name
            or self._substances_table_name
            or self._coatings_table_name
        ):
            config = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(
                self._material_universe_table_name,
                self._in_house_materials_table_name,
                self._specifications_table_name,
                self._products_and_parts_table_name,
                self._substances_table_name,
                self._coatings_table_name,
            )
            return config

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
        return query.run_query(api_method, self._db_key, self._query_config)


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
