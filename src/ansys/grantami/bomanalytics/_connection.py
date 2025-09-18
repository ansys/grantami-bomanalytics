# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Connection to the Granta MI Service Layer.

This module creates the connection object by subclassing the
abstract ``ApiClientFactory`` class in the ``ansys-openapi-common`` package.

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
    Default database key for the Restricted Substances database. This is used if an alternative database
    key isn't specified.
SERVICE_PATH : str
    Location of the BoM Analytics service within the Service Layer web application.
MI_AUTH_PATH : str
    Location of a service that prompts for authorization.
GRANTA_APPLICATION_NAME_HEADER : str
    Identifier used internally by the Granta MI Server.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, overload

from ansys.grantami.bomanalytics_openapi.v2 import api, models
from ansys.openapi.common import (
    ApiClient,
    ApiClientFactory,
    ApiException,
    SessionConfiguration,
    generate_user_agent,
)

from ._exceptions import LicensingException
from ._item_results import ItemResultFactory
from ._logger import logger

DEFAULT_DBKEY = "MI_Restricted_Substances"
SERVICE_PATH = "/BomAnalytics/v2.svc"
MI_AUTH_PATH = "/Health/v2.svc"
GRANTA_APPLICATION_NAME_HEADER = "PyGranta BoM Analytics"

MINIMUM_BAS_VERSION = (24, 2)

if TYPE_CHECKING:
    from ._item_results import Licensing
    from ._query_results import (
        BomComplianceQueryResult,
        BomImpactedSubstancesQueryResult,
        BomSustainabilityQueryResult,
        BomSustainabilitySummaryQueryResult,
        MaterialComplianceQueryResult,
        MaterialImpactedSubstancesQueryResult,
        PartComplianceQueryResult,
        PartImpactedSubstancesQueryResult,
        ResultBaseClass,
        SpecificationComplianceQueryResult,
        SpecificationImpactedSubstancesQueryResult,
        SubstanceComplianceQueryResult,
    )
    from .queries import (
        BomComplianceQuery,
        BomImpactedSubstancesQuery,
        BomSustainabilityQuery,
        BomSustainabilitySummaryQuery,
        MaterialComplianceQuery,
        MaterialImpactedSubstancesQuery,
        PartComplianceQuery,
        PartImpactedSubstancesQuery,
        SpecificationComplianceQuery,
        SpecificationImpactedSubstancesQuery,
        SubstanceComplianceQuery,
        _BaseQuery,
    )


class Connection(ApiClientFactory):
    """Connects to an instance of Granta MI.

    This is a subclass of the :class:`ansys.openapi.common.ApiClientFactory` class.
    All methods in this class are documented as returning :class:`~ansys.openapi.common.ApiClientFactory`
    class instances of the :class:`ansys.grantami.bomanalytics.Connection` class instead.

    Parameters
    ----------
    api_url : str
       Base URL of the API server.
    session_configuration : :class:`~ansys.openapi.common.SessionConfiguration`, optional
       Additional configuration settings for the requests session. The default is ``None``, in which case the
       :class:`~ansys.openapi.common.SessionConfiguration` class with default parameters is used.

    Notes
    -----
    For advanced usage, including configuring session-specific properties and timeouts, see the
    :external+openapi-common:doc:`ansys-openapi-common API reference <api/index>`. Specifically, see the
    documentation for the :class:`~ansys.openapi.common.ApiClientFactory` base class and the
    :class:`~ansys.openapi.common.SessionConfiguration` class.

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
        session_configuration.headers["X-Granta-ActAsReadUser"] = "true"

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
        ConnectionError
            If the resulting client cannot connect to the BoM Analytics service.
        LicensingException
            Error raised if no licenses were found.
        """

        self._validate_builder()
        client = BomAnalyticsClient(
            session=self._session,
            servicelayer_url=self._base_servicelayer_url,
            configuration=self._session_configuration,
        )
        client.setup_client(models)
        self._test_connection(client)
        return client

    @staticmethod
    def _test_connection(client: "BomAnalyticsClient") -> None:
        """Check if the created client can be used to perform a query.

        This method checks for the licensing details, because it is a GET query that does not require parameters.
        It specifically checks for a 404 error, which most likely means that the BoM Analytics
        service is not available, or is not the expected minimum version.

        Parameters
        ----------
        client : :class:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient`
            Client object to test.

        Raises
        ------
        ConnectionError
            Error raised if the test query fails.
        LicensingException
            Error raised if no licenses were found.
        """
        try:
            licenses = client._get_licensing_information()
        except ApiException as e:
            if e.status_code == 404:
                raise ConnectionError(
                    "Cannot find the BoM Analytics service in Granta MI Service Layer. Ensure a compatible version of "
                    "the Restricted Substances And Sustainability Reports are available on the server and try again. "
                    "The minimum required Restricted Substances And Sustainability Reports version is "
                    f"{'.'.join([str(e) for e in MINIMUM_BAS_VERSION])}."
                )
            else:
                raise ConnectionError(
                    "An unexpected error occurred when trying to connect to BoM Analytics service in Granta MI Service "
                    "Layer. Check the Service Layer logs for more information and try again."
                )
        if not licenses.restricted_substances and not licenses.sustainability:
            raise LicensingException(
                "The connection to BoM Analytics Services was successful, but there are no valid licenses for either "
                "restricted substances or sustainability. Contact your Granta MI administrator."
            )


class BomAnalyticsClient(ApiClient):
    """Communicates with Granta MI. This class is instantiated by the
    :class:`~ansys.grantami.bomanalytics.Connection` class described earlier and should not be instantiated directly.
    """

    def __init__(self, servicelayer_url: str, **kwargs: Any) -> None:
        self._sl_url: str = servicelayer_url.strip("/")
        sl_url_with_service = self._sl_url + SERVICE_PATH
        logger.debug("Creating BomAnalyticsClient")
        logger.debug(f"Base Service Layer URL: {self._sl_url}")
        logger.debug(f"Service URL: {sl_url_with_service}")

        super().__init__(api_url=sl_url_with_service, **kwargs)

        self._db_key: str = DEFAULT_DBKEY
        self._table_names: Dict[str, Optional[str]] = {
            "material_universe_table_name": None,
            "inhouse_materials_table_name": None,
            "specifications_table_name": None,
            "products_and_parts_table_name": None,
            "substances_table_name": None,
            "coatings_table_name": None,
        }
        self._max_spec_depth: Optional[int] = None

    def __repr__(self) -> str:
        max_link_value: Union[str, int] = (
            "unlimited" if self.maximum_spec_link_depth is None else self.maximum_spec_link_depth
        )
        repr_entries: List[Tuple[str, Union[str, int, None]]] = [
            ("url", self._sl_url),
            ("maximum_spec_link_depth", max_link_value),
            ("dbkey", self._db_key),
        ]
        for k, v in self._table_names.items():
            if v:
                repr_entries.append((k, v))
        rendered_entries = []
        for name, value in repr_entries:
            if isinstance(value, str):
                value = f'"{value}"'
            rendered_entries.append(f"{name}={value}")
        return f'<BomAnalyticsClient: {", ".join(rendered_entries)}>'

    @property
    def maximum_spec_link_depth(self) -> Optional[int]:
        """Maximum number of specification-to-specification links that are followed when processing
        a query. If a maximum is specified, specification-to-specification links are truncated at the
        specified depth, and only coatings and substances identified up to and including that point are
        included in the analysis.

        The default is ``None``, in which case no limit is applied to the number of specification-to-specification
        links. This might lead to performance issues if there are large numbers of specification-to-specification
        links present in the database.

        This parameter is supported with Restricted Substances Reports 2023 R2 and later. With older reports,
        this parameter has no effect, all specification-to-specification links are followed.

        .. versionadded:: 1.2

        .. note::
            This limit applies to each branch of the BoM individually. This is not a global limit on the number of
            specification-to-specification links that are traversed across the entire BoM. Instead, it is a limit on
            the maximum depth of specifications below any individual specification node.

        Returns
        -------
        Optional[int]
            Maximum depth of specification-to-specification links that are followed.

        """
        return self._max_spec_depth

    @maximum_spec_link_depth.setter
    def maximum_spec_link_depth(self, value: Optional[int]) -> None:
        if value is not None and value < 0:
            raise ValueError("maximum_spec_link_depth must be a non-negative integer or None")
        self._max_spec_depth = value

    def set_database_details(
        self,
        database_key: str = DEFAULT_DBKEY,
        material_universe_table_name: Optional[str] = None,
        in_house_materials_table_name: Optional[str] = None,
        specifications_table_name: Optional[str] = None,
        products_and_parts_table_name: Optional[str] = None,
        substances_table_name: Optional[str] = None,
        coatings_table_name: Optional[str] = None,
        process_universe_table_name: Optional[str] = None,
        location_table_name: Optional[str] = None,
        transport_table_name: Optional[str] = None,
    ) -> None:
        """Configure the database key and table names if different from the defaults.

        The ``database_key`` argument is required if Granta MI is configured to use a value other than
        ``MI_Restricted_Substances`` for the Restricted Substances and Sustainability database.

        A ``table_name`` argument is required for each table in the Restricted Substances and Sustainability database
        that has been renamed.

        If external records are used in any analysis, the database key for those records should not be provided here.
        Instead, it should be provided in the appropriate query build method or in the XML BoM. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        database_key : str, optional
            Database key for the Restricted Substances and Sustainability database. The default is ``None``,
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
        process_universe_table_name : str, optional
            Name of the table that implements the ``ProcessUniverse`` schema. The default
            is ``None``, in which case  ``ProcessUniverse`` is used.
        location_table_name : str, optional
            Name of the table that implements the ``Locations`` schema. The default
            is ``None``, in which case  ``Locations`` is used.

            .. versionadded:: 2.0
        transport_table_name : str, optional
            Name of the table that implements the ``Transport`` schema. The default
            is ``None``, in which case  ``Transport`` is used.

            .. versionadded:: 2.0

        Notes
        -----
        The database key and table names are configurable, but they only need to be specified if they have been modified
        from the defaults. Here are the default key and table names:

        * Database key: MI_Restricted_Substances
        * Table names:

          - MaterialUniverse
          - Materials - in house
          - Specifications
          - Products and parts
          - Restricted Substances
          - Coatings
          - ProcessUniverse
          - Locations
          - Transport

        Examples
        --------
        >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
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
        self._table_names["process_universe_table_name"] = process_universe_table_name
        self._table_names["locations_table_name"] = location_table_name
        self._table_names["transport_table_name"] = transport_table_name

    @overload
    def run(self, query: "MaterialImpactedSubstancesQuery") -> "MaterialImpactedSubstancesQueryResult": ...

    @overload
    def run(self, query: "MaterialComplianceQuery") -> "MaterialComplianceQueryResult": ...

    @overload
    def run(self, query: "PartImpactedSubstancesQuery") -> "PartImpactedSubstancesQueryResult": ...

    @overload
    def run(self, query: "PartComplianceQuery") -> "PartComplianceQueryResult": ...

    @overload
    def run(self, query: "SpecificationImpactedSubstancesQuery") -> "SpecificationImpactedSubstancesQueryResult": ...

    @overload
    def run(self, query: "SpecificationComplianceQuery") -> "SpecificationComplianceQueryResult": ...

    @overload
    def run(self, query: "SubstanceComplianceQuery") -> "SubstanceComplianceQueryResult": ...

    @overload
    def run(self, query: "BomImpactedSubstancesQuery") -> "BomImpactedSubstancesQueryResult": ...

    @overload
    def run(self, query: "BomComplianceQuery") -> "BomComplianceQueryResult": ...

    @overload
    def run(self, query: "BomSustainabilityQuery") -> "BomSustainabilityQueryResult": ...

    @overload
    def run(self, query: "BomSustainabilitySummaryQuery") -> "BomSustainabilitySummaryQueryResult": ...

    def run(self, query: "_BaseQuery") -> "ResultBaseClass":
        """Run a query against the Granta MI database.

        Parameters
        ----------
        query
            A compliance, impacted substances, or sustainability query object.

        Returns
        -------
        Query Result
            Specific result object based on the provided query, which contains either the compliance,
            impacted substances, or sustainability results.

        Raises
        ------
        :class:`~ansys.grantami.bomanalytics.GrantaMIException`
            Error raised if the server encounters an error while processing the query with a severity
            of ``critical``. This indicates that Granta MI is running and the BoM Analytics service
            is available, but the query could not be run, probably because of a missing database or table.
        :class:`~ansys.openapi.common.ApiException`
            Error raised if the Granta MI server is not able to return a response, probably
            because of an internal configuration error or the BoM Analytics service not being installed.
        """

        logger.info(f"Running query {query} with connection {self}")
        api_instance = query.api_class(self)
        return query._run_query(api_instance=api_instance, static_arguments=self._query_arguments)

    @property
    def _query_arguments(
        self,
    ) -> Dict[str, Union[str, models.CommonRequestConfig]]:
        """Generate the connection-level arguments for a query, such as the database key and table names.

        Query-specific arguments (such as records and legislations) are added within the query object itself.

        Returns
        -------
        arguments
            Dictionary of `**kwargs` to use to run a query.

        Notes
        -----
        The table mapping configuration object is only created if at least one table has a non-default name.
        The low-level API understands ``{"config": None}`` to mean that default table names are in use.

        The database key is always required. The default is only included here for convenience.
        """

        config = models.CommonRequestConfig()
        if self._max_spec_depth is not None:
            logger.info(f"Using maximum specification-to-specification link depth: {self._max_spec_depth}")
            config.maximum_spec_chain_node_count = self._max_spec_depth + 1
        else:
            logger.info(f"No specification-to-specification link depth limit is specified. All links will be followed.")
        if any(self._table_names.values()):
            for table_type, name in self._table_names.items():
                if name is not None:
                    setattr(config, table_type, name)
            table_mapping = [f"{n}: {v}" for n, v in self._table_names.items() if v]
            logger.info(f"Using custom table config:")
            for line in table_mapping:
                logger.info(line)
        else:
            logger.info(f"Using default table config")

        if self._db_key != DEFAULT_DBKEY:
            logger.info(f"Using custom database key: {self._db_key}")
        else:
            logger.info(f"Using default database key ({self._db_key})")

        arguments: Dict[str, Union[str, models.CommonRequestConfig]] = {"config": config, "database_key": self._db_key}
        return arguments

    def _get_licensing_information(self) -> "Licensing":
        """
        Get licensing information from the server.

        Returns
        -------
        :class:`~ansys.grantami.bomanalytics._item_results.Licensing`
        """
        api_instance = api.LicensesApi(self)
        response = api_instance.get_licenses()
        return ItemResultFactory.create_licensing_result(response)

    def _get_yaml(self) -> str:
        """
        Get the OpenAPI document for the BoM Analytics Services API.

        Returns
        -------
        str
        """
        api_instance = api.DocumentationApi(self)
        result: str = api_instance.get_yaml()
        return result
