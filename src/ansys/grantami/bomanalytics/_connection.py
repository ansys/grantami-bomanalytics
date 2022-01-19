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

from typing import overload, TYPE_CHECKING, Union, Dict, Optional, Type, Any

from ansys.openapi import common  # type: ignore[import]
from ansys.grantami.bomanalytics_openapi import models  # type: ignore[import]
from ._logger import logger

DEFAULT_DBKEY = "MI_Restricted_Substances"
SERVICE_PATH = "/BomAnalytics/v1.svc"
OIDC_HEADER_APPLICATION_NAME = "MI Scripting Toolkit"

if TYPE_CHECKING:
    from .queries import (
        MaterialImpactedSubstancesQuery,
        MaterialComplianceQuery,
        PartImpactedSubstancesQuery,
        PartComplianceQuery,
        SpecificationImpactedSubstancesQuery,
        SpecificationComplianceQuery,
        SubstanceComplianceQuery,
        BomImpactedSubstancesQuery,
        BomComplianceQuery,
        Yaml,
    )
    from ._query_results import (
        MaterialImpactedSubstancesQueryResult,
        MaterialComplianceQueryResult,
        PartImpactedSubstancesQueryResult,
        PartComplianceQueryResult,
        SpecificationImpactedSubstancesQueryResult,
        SpecificationComplianceQueryResult,
        SubstanceComplianceQueryResult,
        BomImpactedSubstancesQueryResult,
        BomComplianceQueryResult,
    )


class Connection(common.ApiClientFactory):
    """Connect to an instance of Granta MI.

    Notes
    -----
    For advanced usage, including configuring session-specific properties and timeouts, see the
    `ansys-openapi-common` package documentation.

    The connection to Granta MI is created in 3 stages:

    1. Create the connection builder object and specify the server to be connected to.
    2. Specify the authentication method to be used for the connection and provide credentials if required.
    3. Connect to the server (the connection object is returned).

    The examples below show this process for different authentication methods.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> cxn
    <BomServicesClient: url=http://my_mi_server/mi_servicelayer>

    >>> cxn = (
    ...     Connection("http://my_mi_server/mi_servicelayer")
    ...     .with_credentials(username="my_username", password="my_password")
    ...     .connect()
    ... )
    >>> cxn
    <BomServicesClient: url=http://my_mi_server/mi_servicelayer>
    """

    def connect(self) -> "BomAnalyticsClient":
        # Use the docstring on the method in the base class.
        self._validate_builder()
        session_configuration = self._session_configuration
        session_configuration.headers["X-Granta-ApplicationName"] = OIDC_HEADER_APPLICATION_NAME
        client = BomAnalyticsClient(
            session=self._session, servicelayer_url=self._api_url, configuration=session_configuration
        )
        client.setup_client(models)
        return client


class BomAnalyticsClient(common.ApiClient):
    """The class used to communicate with Granta MI. It is instantiated by the
    :class:`~ansys.grantami.bomanalytics.Connection` class defined above, and should not be instantiated directly.
    """

    def __init__(self, servicelayer_url: str, **kwargs: Any) -> None:
        self._sl_url = servicelayer_url.strip("/")
        sl_url_with_service = self._sl_url + SERVICE_PATH
        logger.debug("Creating BomAnalyticsClient")
        logger.debug(f"Base Service Layer URL: {self._sl_url}")
        logger.debug(f"Service URL: {sl_url_with_service}")
        super().__init__(api_url=sl_url_with_service, **kwargs)

        self._db_key = DEFAULT_DBKEY
        self._table_names: Dict[str, Optional[str]] = {
            "material_universe_table_name": None,
            "inhouse_materials_table_name": None,
            "specifications_table_name": None,
            "products_and_parts_table_name": None,
            "substances_table_name": None,
            "coatings_table_name": None,
        }

    def __repr__(self) -> str:
        base_repr = f'<BomServicesClient: url="{self._sl_url}", dbkey="{self._db_key}"'
        custom_tables = ", ".join([f'{k}="{v}"' for k, v in self._table_names.items() if v])
        if custom_tables:
            return base_repr + f", {custom_tables}>"
        else:
            return base_repr + ">"

    def set_database_details(
        self,
        database_key: str = DEFAULT_DBKEY,
        material_universe_table_name: Optional[str] = None,
        in_house_materials_table_name: Optional[str] = None,
        specifications_table_name: Optional[str] = None,
        products_and_parts_table_name: Optional[str] = None,
        substances_table_name: Optional[str] = None,
        coatings_table_name: Optional[str] = None,
    ) -> None:
        """Configure the database key and table names, if different from the defaults.

        Database key is required if Granta MI is configured to use a value other than 'MI_Restricted_Substances'. A
        table name is required if it has been modified from the defaults.

        Parameters
        ----------
        database_key : Optional[str]
            The database key for the Restricted Substances database.
        material_universe_table_name : Optional[str]
            The name of the table that implements the 'MaterialUniverse' schema.
        in_house_materials_table_name : Optional[str]
            The name of the table that implements the 'Materials - in house' schema.
        specifications_table_name : Optional[str]
            The name of the table that implements the 'Specifications' schema.
        products_and_parts_table_name : Optional[str]
            The name of the table that implements the 'Products and parts' schema.
        substances_table_name : Optional[str]
            The name of the table that implements the 'Restricted Substances' schema.
        coatings_table_name : Optional[str]
            The name of the table that implements the 'Coatings' schema.

        Notes
        -----
        The database key and table names are configurable, but only need to be specified if they have been modified
        from the defaults. These are summarized below:

        * Database key: MI_Restricted_Substances
        * Table names:

          - MaterialUniverse
          - Materials - in house
          - Specifications
          - Products and parts
          - Restricted Substances
          - Coatings

        Examples
        --------
        >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
        >>> cxn.set_database_details(database_key = "MY_RS_DB",
        ...                          in_house_materials_table_name = "My Materials")
        """

        self._db_key = database_key
        self._table_names["material_universe_table_name"] = material_universe_table_name
        self._table_names["inhouse_materials_table_name"] = in_house_materials_table_name
        self._table_names["specifications_table_name"] = specifications_table_name
        self._table_names["products_and_parts_table_name"] = products_and_parts_table_name
        self._table_names["substances_table_name"] = substances_table_name
        self._table_names["coatings_table_name"] = coatings_table_name

    @overload
    def run(self, query: "MaterialImpactedSubstancesQuery") -> "MaterialImpactedSubstancesQueryResult":
        ...

    @overload
    def run(self, query: "MaterialComplianceQuery") -> "MaterialComplianceQueryResult":
        ...

    @overload
    def run(self, query: "PartImpactedSubstancesQuery") -> "PartImpactedSubstancesQueryResult":
        ...

    @overload
    def run(self, query: "PartComplianceQuery") -> "PartComplianceQueryResult":
        ...

    @overload
    def run(self, query: "SpecificationImpactedSubstancesQuery") -> "SpecificationImpactedSubstancesQueryResult":
        ...

    @overload
    def run(self, query: "SpecificationComplianceQuery") -> "SpecificationComplianceQueryResult":
        ...

    @overload
    def run(self, query: "SubstanceComplianceQuery") -> "SubstanceComplianceQueryResult":
        ...

    @overload
    def run(self, query: "BomImpactedSubstancesQuery") -> "BomImpactedSubstancesQueryResult":
        ...

    @overload
    def run(self, query: "BomComplianceQuery") -> "BomComplianceQueryResult":
        ...

    @overload
    def run(self, query: "Yaml") -> str:
        ...

    @overload
    def run(self, query: Type["Yaml"]) -> str:
        ...

    def run(self, query):  # type: ignore[no-untyped-def]
        """Run a query against the Granta MI database.

        Parameters
        ----------
        query
            A compliance, impacted substance, or yaml query object.

        Returns
        -------
        Query Result
            The specific result object based on the provided query, which contains either the compliance or
            impacted substances results. In the case of a yaml query, returns a string.

        Raises
        ------
        :class:`~ansys.grantami.bomanalytics.GrantaMIException`
            [TECHDOCS] If a message is returned with a severity of "critical". Granta MI is running and the BoM
            Analytics Service is available, but it was not able to run the query. Possible causes include a missing
            database or table.
        :class:`~ansys.openapi.common.ApiException`
            [TECHDOCS] If the Granta MI server was not able to return a response. Possible causes include an internal
            configuration error, or that the BoM Analytics Service is not installed.
        """

        logger.info(f"Running query {query} with connection {self}")
        api_instance = query.api_class(self)
        return query._run_query(api_instance=api_instance, static_arguments=self._query_arguments)

    @property
    def _query_arguments(
        self,
    ) -> Dict[str, Union[str, models.CommonRequestConfig, None]]:
        """Generate the connection-level arguments for a query, i.e. the database key and table names.

        Query-specific arguments (records, legislations, etc.) are added within the query object itself.

        Returns
        -------
        arguments
            A dictionary of `**kwargs` to be used to run a query.

        Notes
        -----
        The table mapping config is only created if at least one table has a non-default name. The low-level API
        understands `{"config": None}` to mean default table names are being used.

        The database key is always required. The default is only included here for convenience.
        """

        if any(self._table_names.values()):
            config = models.CommonRequestConfig(**self._table_names)
            table_mapping = [f"{n}: {v}" for n, v in self._table_names.items() if v]
            logger.info(f"Using custom table config:")
            for line in table_mapping:
                logger.info(line)
        else:
            config = None
            logger.info(f"Using default table config")

        if self._db_key != DEFAULT_DBKEY:
            logger.info(f"Using custom database key: {self._db_key}")
        else:
            logger.info(f"Using default database key ({self._db_key})")

        arguments = {"config": config, "database_key": self._db_key}
        return arguments
