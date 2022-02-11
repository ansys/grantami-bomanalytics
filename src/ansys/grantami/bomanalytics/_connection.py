""" Connection to Granta MI Service layer.

This module creates the connection object by subclassing the
abstract ``ApiClientFactory`` in the ``auth_common`` package.

The connection object itself is also subclassed to include global configuration
options that span all queries and the method to execute the query.

Parameters
----------
api_url : str
    URL to Granta MI.
session_configuration
    Configuration settings for the session.

Attributes
----------
DEFAULT_DBKEY : str
    Default database key for the Restricted Substances Database. This is used if an alternative database
    key isn't specified.
"""

from typing import overload, TYPE_CHECKING, Union, Dict, Optional, Type, Any

from ansys.openapi.common import (  # type: ignore[import]
    ApiClientFactory,
    ApiClient,
    generate_user_agent,
    SessionConfiguration,
)
from ansys.grantami.bomanalytics_openapi import models  # type: ignore[import]
from ._logger import logger

DEFAULT_DBKEY = "MI_Restricted_Substances"
SERVICE_PATH = "/BomAnalytics/v1.svc"
MI_AUTH_PATH = "/Health/v2.svc"
GRANTA_APPLICATION_NAME_HEADER = "MI Scripting Toolkit"


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


class Connection(ApiClientFactory):
    """Connects to an instance of Granta MI.

    This is a subclass of :class:`ansys.openapi.common.ApiClientFactory`. All methods within this class that are
    documented as returning :class:`~ansys.openapi.common.ApiClientFactory` return instances of
    :class:`ansys.grantami.bomanalytics.Connection` instead.

    Parameters
    ----------
    api_url : str
       Base URL of the API server.
    session_configuration : :class:`~ansys.openapi.common.SessionConfiguration`, optional
       Additional configuration settings for the requests session. The default is ``None``, in which case the
       class :class:`~ansys.openapi.common.SessionConfiguration` with default parameters is used.

    Notes
    -----
    For advanced usage, including configuring session-specific properties and timeouts, see
    :external+openapi-common:doc:`ansys-openapi-common API Reference <api/index>`. Specifically, the documentation on
    the base class :class:`~ansys.openapi.common.ApiClientFactory` and the class
    :class:`~ansys.openapi.common.SessionConfiguration`.

    To create the connection to Granta MI, you perform three steps:

    1. Create the connection builder object and specify the server to connect to.
    2. Specify the authentication method to use for the connection and provide credentials if required.
    3. Connect to the server, which returns the connection object.

    The examples show this process for different authentication methods.

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

    def __init__(self, api_url: str, session_configuration: Optional[SessionConfiguration] = None) -> None:
        from . import __version__

        auth_url = api_url.strip("/") + MI_AUTH_PATH
        super().__init__(auth_url, session_configuration)
        self._base_servicelayer_url = api_url
        session_configuration = self._session_configuration
        session_configuration.headers["X-Granta-ApplicationName"] = GRANTA_APPLICATION_NAME_HEADER
        session_configuration.headers["User-Agent"] = generate_user_agent("ansys-grantami-bomanalytics", __version__)

    def connect(self) -> "BomAnalyticsClient":
        """Finalize the BoM Analytics client and return it for use.

        Authentication must be configured for this method to succeed.

        Returns
        -------
        :class:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient`
            Client object that can be used to connect to Granta MI and perform BoM Analytics operations.

        Raises
        ------
        ValueError
            When the client is not fully configured.
        """

        self._validate_builder()
        client = BomAnalyticsClient(
            session=self._session,
            servicelayer_url=self._base_servicelayer_url,
            configuration=self._session_configuration,
        )
        client.setup_client(models)
        return client


class BomAnalyticsClient(ApiClient):
    """Communicates with Granta MI. This class is instantiated by the
    :class:`~ansys.grantami.bomanalytics.Connection` class defined above and should not be instantiated directly.
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
        """Configure the database key and table names if different from the defaults.

        A database key is required if Granta MI is configured to use a value other than ``MI_Restricted_Substances``.
        A table name is required for each table in the Restricted Substances Database that has been renamed.

        Parameters
        ----------
        database_key : str, optional
            Database key for the Restricted Substances database. The default is ``None``,
            in which case ``MI_Restricted_Substances`` is used.
        material_universe_table_name : str, optional
            Name of the table that implements the ``MaterialUniverse`` schema. The
            default is ``None``, in which case ``MaterialUniverse`` is used.
        in_house_materials_table_name : str, optional
            Name of the table that implements the ``Materials - in house`` schema.
            The default is ``None``, in which case ``Materials - in house`` is used.
        specifications_table_name : str, optional
            Name of the table that implements the ``Specifications`` schema. The
            default is ``None``, in which case ``Specifications`` is used.
        products_and_parts_table_name : str, optional
            Name of the table that implements the ``Products and parts`` schema. The
            default is ``None``, in which case ``Products and parts`` is used.
        substances_table_name : str, optional
            Name of the table that implements the ``Restricted Substances`` schema.
            The default is ``None``, in which case ``Restricted Substances`` is used.
        coatings_table_name : str, optional
            Name of the table that implements the ``Coatings`` schema. The default
            is ``None``, in which case  ``Coatings`` is used.

        Notes
        -----
        The database key and table names are configurable, but they only need to be specified if they have been modified
        from the defaults. Here is a summary of the default names:

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
            impacted substances results. In the case of a yaml query, a string is returned.

        Raises
        ------
        :class:`~ansys.grantami.bomanalytics.GrantaMIException`
            If the server encounters an error while processing the query with a severity of 'critical'. This indicates
            that Granta MI is running and the BoM Analytics Service is available, but the query could not be run,
            probably because of a missing database or table.
        :class:`~ansys.openapi.common.ApiException`
            If this exception is raised, the Granta MI server was not able to return a response, probably
            because of an internal configuration error or the BoM Analytics Service not being installed.
        """

        logger.info(f"Running query {query} with connection {self}")
        api_instance = query.api_class(self)
        return query._run_query(api_instance=api_instance, static_arguments=self._query_arguments)

    @property
    def _query_arguments(
        self,
    ) -> Dict[str, Union[str, models.CommonRequestConfig, None]]:
        """Generate the connection-level arguments for a query, such as the database key and table names.

        Query-specific arguments (such as records and legislations) are added within the query object itself.

        Returns
        -------
        arguments
            A dictionary of `**kwargs` to use to run a query.

        Notes
        -----
        The table mapping configuration object is only created if at least one table has a non-default name.
        The low-level API understands ``{"config": None}`` to mean that default table names are in use.

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
