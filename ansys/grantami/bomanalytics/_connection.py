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

from typing import overload, TYPE_CHECKING, Union, Dict, Optional, Type, Tuple
import logging
from ansys.openapi import common  # type: ignore[import]
from ansys.grantami.bomanalytics_codegen import models  # type: ignore[import]

DEFAULT_DBKEY = "MI_Restricted_Substances"

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

logger = logging.getLogger(__name__)


class Connection(common.ApiClientFactory):
    """Build a connection to an instance of Granta MI.

    Parameters
    ----------
    servicelayer_url
        The url of the Granta MI Service layer.

    Notes
    -----
    For advanced usage, including configuring any session-specific properties and timeouts, see the documentation of
    the *auth_common* package.

    This a builder class, which means you must call the `.build()` method to return the actual
    connection object.

    Builder classes are generally instantiated, configured, and then built. The examples below
    show this in action, first by instantiating the Connection builder (i.e. `Connection()`),
    then configuring the builder object (`.with_autologon()`), and then using the builder
    object to build the connection itself (`.build()`).

    Examples
    --------
    >>> Connection("http://my_mi_server/mi_servicelayer").with_autologon().build()
    <BomServicesClient: url=http://my_mi_server/mi_servicelayer>

    >>> cxn = (
    ...     Connection("http://my_mi_server/mi_servicelayer")
    ...     .with_credentials(username="my_username", password="my_password")
    ...     .build()
    ... )
    >>> cxn
    <BomServicesClient: url=http://my_mi_server/mi_servicelayer>
    """

    def build(self) -> "BomAnalyticsClient":
        # Use the docstring on the method in the base class.
        self._validate_builder()
        client = BomAnalyticsClient(self._session, self._sl_url, self._session_configuration)
        client.setup_client(models)
        return client


class BomAnalyticsClient(common.ApiClient):
    def __init__(self, *args: Tuple, **kwargs: Dict) -> None:
        super().__init__(*args, **kwargs)
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
        base_repr = f'<BomServicesClient: url="{self.api_url}", dbkey="{self._db_key}"'
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

        The database key is required if something other than MI_Restricted_Substances is being used. A table name should
        only be specified if it has been modified from the defaults.

        Parameters
        ----------
        database_key
            The database key for the Restricted Substances database.
        material_universe_table_name
            The name of the table that implements the 'MaterialUniverse' schema.
        in_house_materials_table_name
            The name of the table that implements the 'Materials - in house' schema.
        specifications_table_name
            The name of the table that implements the 'Specifications' schema.
        products_and_parts_table_name
            The name of the table that implements the 'Products and parts' schema.
        substances_table_name
            The name of the table that implements the 'Restricted Substances' schema.
        coatings_table_name
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
        >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
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
        """

        logger.info(f"[TECHDOCS] Running query {query} with connection {self}")
        api_instance = query.api_class(self)
        return query._run_query(api_instance=api_instance, static_arguments=self._query_arguments)

    @property
    def _query_arguments(
        self,
    ) -> Dict[str, Union[str, models.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig, None]]:
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
            config = models.GrantaBomAnalyticsServicesInterfaceCommonRequestConfig(**self._table_names)
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
