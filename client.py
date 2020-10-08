# -*- coding: utf-8 -*-
#
# This file is part of asencis.
#
# Copyright (C) 2020 asencis.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""
    Python API wrapper for the DataCite RESTful API service
    Using: v.2.0: January 7, 2019, new API endpoints, using camelCase for attributes
    Docs: [https://support.datacite.org/reference/introduction, https://support.datacite.org/docs/api]
"""
import io
import os
import gzip
import json
import time
import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from .exceptions import *

class DataciteRESTAPIClient(object):

    """
    DataCite RESTful API client wrapper.
    Docs: [https://support.datacite.org/reference/introduction]
    The DataCite REST API returns information about DataCite content.
    The API is RESTFUL and returns results in JSON.
    It follows the JSONAPI specification.
    The mime-type for API results is application/vnd.api+json.
    """

    def __init__(self, url, username, password):
        """
        The base DataciteRESTAPIClient class

        @param username: DataCite username.
        @param password: DataCite password.
        @param url: DataCite RESTful API base URL. Defaults to https://api.datacite.org/.

        Returns object with appended url, username and password attributes.
        """
        self.url = url
        self.headers = {
            'Content-Type': 'application/vnd.api+json'
        }
        self.action = None
        self.username = username
        self.password = password

    def create_or_update_doi(self, data, doi):
        """"
        Method to "mint" a new DOI, or update it if it already exists.

        @param doi: DOI name for the target resource.
        @param data: this is the body payload which is a JSON serialized version of the DOI object

        Returns a tuple of created, update Boolean flags and response object
        """

        self.action = 'create_doi'

        response = None

        created = False

        updated = False

        try:
            response = requests.post(
                '{}/dois'.format(self.url),
                data=data,
                headers=self.headers,
                auth=HTTPBasicAuth(self.username, self.password),
            )

            response.raise_for_status()

            created = True

        except requests.exceptions.HTTPError as exception:
            if response.status_code == 422:
                response = requests.put(
                    '{}/dois/{}'.format(self.url, doi),
                    data=data,
                    headers=self.headers,
                    auth=HTTPBasicAuth(self.username, self.password),
                )

                response.raise_for_status()

                updated = True

        return created, updated, response

    def delete_doi(self, doi):
        """"
        Method to deleted a DOI if it exists.

        @param doi: DOI name for the target resource.

        Returns a tuple of deleted Boolean flag and response object
        """

        self.action = 'delete_doi'

        response = None

        deleted = False

        try:
            response = requests.delete(
                '{}/dois/{}'.format(self.url, doi),
                headers=headers,
                auth=HTTPBasicAuth(self.username, self.password),
            )

            response.raise_for_status()

            deleted = True

        except requests.exceptions.HTTPError as exception:
            deleted = False

        return deleted, response

class DataciteUsageReportsAPIClient(object):
    """
    DataCite Usage Reports RESTful API client wrapper.
    Docs: [https://support.datacite.org/docs/usage-reports-api-guide]
    The DataCite Usage Reports API allows repositories to store data usage metrics.
    The API requires authentication for most writing endpoints but all reading endpoints are accessible without credentials.
    The API is RESTFUL and returns results in JSON.
    It follows the JSONAPI specification.
    The mime-type for API results is application/vnd.api+json.
    """

    def __init__(self, url, bearer):
        """
        The base DataciteUsageReportAPIClient class

        @param key: DataCite API Key.
        @param url: DataCite UsageReports RESTful API base URL. Defaults to https://api.datacite.org/.

        Returns object with appended url, username and password attributes.
        """
        self.url = url
        self.bearer = bearer

        if not self.bearer:
            raise DataciteAPIAuthenticationError

        self.headers = {
            'Content-Type': 'application/gzip',
            'Content-Encoding': 'gzip',
            'Accept': 'gzip',
            'Authorization': f'Bearer {self.bearer}'
        }
        self.action = None
        self.maximum_attempts_on_failure = 10

    def retry_on_failure(url, method, data, headers, *args, **kwargs):
        response = None

        for attempt in range(self.maximum_attempts_on_failure):
            try:
                response = getattr(requests, method)(
                    url,
                    data=gzip.compress(data.encode()),
                    headers=headers,
                )

                response.raise_for_status()

                return response
            except requests.exceptions.HTTPError as exception:
                print(f'{response.status_code}: {exception}')
                time.sleep(1)

        return response

    def create_or_update_report(self, filepath, uuid, *args, **kwargs):
        """"
        Method to submit a compressed usage report

        @param uuid UUID which matches to the report UUID, this is required
        """

        # $ curl --header "Content-Type: application/gzip; Content-Encoding: gzip" -H "Authorization: Bearer {YOUR-JSON-WEB-TOKEN}" -X POST https://api.datacite.org/reports/ -d @usage-report-compressed

        if not uuid:
            raise DataciteCompressedReportUUIDMissingError
        else:
            self.uuid = uuid

        self.action = 'send_compressed_usage_report'

        # It's generally best to send a report as compressed, as it is not clear what the cut off point is for large reports:
        with io.open(f'{filepath}', 'r', encoding='utf-8') as file:
            data = file.read()

        # This method is a retry since the Datacite REST Usage Report API gives many 500 errors:
        return retry_if_500(url='{}/reports/{}'.format(self.url, self.uuid), method='PUT', data=data, headers=self.headers)
