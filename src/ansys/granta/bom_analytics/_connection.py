""" Connection to Granta MI Service layer.

This module subclasses creates the connection object by subclassing the
abstract `ApiClientFactory` in the `auth_common` package.

The connection object itself is also subclassed to include global configuration
options that span all queries, and the method to execute the query.

Attributes
----------
DEFAULT_DBKEY : str
    The default database key for Restricted Substances. Used if a database key isn't specified.
"""

from typing import overload, TYPE_CHECKING, Union, Dict
import logging
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

logger = logging.getLogger(__name__)


class BomServicesClient(auth_common.ApiClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db_key = DEFAULT_DBKEY
        self._table_names: Dict[str, Union[str, None]] = {
            "material_universe_table_name": None,
            "inhouse_materials_table_name": None,
            "specifications_table_name": None,
            "products_and_parts_table_name": None,
            "substances_table_name": None,
            "coatings_table_name": None,
        }

    def __repr__(self):
        return f"<BomServicesClient: url={self.api_url}>"

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
        """Configure the database key and table names if the defaults in Granta MI have been modified.

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
        self._table_names["material_universe_table_name"] = material_universe_table_name
        self._table_names["inhouse_materials_table_name"] = in_house_materials_table_name
        self._table_names["specifications_table_name"] = specifications_table_name
        self._table_names["products_and_parts_table_name"] = products_and_parts_table_name
        self._table_names["substances_table_name"] = substances_table_name
        self._table_names["coatings_table_name"] = coatings_table_name

    @property
    def _query_arguments(
        self,
    ) -> Dict[str, Union[str, bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig, None]]:
        """:obj:`dict`: A dictionary of ``**kwargs`` to be used to run a query.

        The arguments returned here are limited to connection-level arguments, i.e. those that relate to the database
        schema. Query-specific arguments (records, legislations, etc.) are added within the query object itself.

        The table mapping config is only created if at least one table has a non-default name.
        """

        if any(self._table_names.values()):
            config = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(**self._table_names)
            table_mapping = [f"{n}: {v}" for n, v in self._table_names.items() if v]
            logger.info(f"[TECHDOCS] Using custom table config:")
            for line in table_mapping:
                logger.info(line)
        else:
            config = None
            logger.info(f"[TECHDOCS] Using default table config")

        if self._db_key != DEFAULT_DBKEY:
            logger.info(f"[TECHDOCS] Using custom database key: {self._db_key}")
        else:
            logger.info(f"[TECHDOCS] Using default database key ({self._db_key})")

        arguments = {"config": config, "database_key": self._db_key}
        return arguments

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
        """Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        query : Query
            A compliance or impacted substance query

        Returns
        -------
        Result
            The corresponding result object based on the provided query
        """

        logger.info(f"[TECHDOCS] Running query {query} with connection {self}")
        api_instance = query.api_class(self)
        return query.run_query(api_instance=api_instance, static_arguments=self._query_arguments)


class Connection(auth_common.ApiClientFactory):
    """ Build a connection to an instance of Granta MI.

    Parameters
    ----------
    servicelayer_url : str
        The url to the Granta MI service layer

    Notes
    -----
    This a builder class, which means you must call the `.build()` method to return the actual
    connection object.

    Builder classes are generally instantiated, configured, and then built. The examples below
    show this in action, first by instantiating the Connection builder (i.e. Connection()),
    then configuring the builder object (.with_autologon()), and then using the builder
    object to build the connection itself (.build()).

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
