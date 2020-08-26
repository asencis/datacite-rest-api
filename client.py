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

import json
import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

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
        self.headers = {'content-type': 'application/vnd.api+json'}
        self.action = None
        self.username = username
        self.password = password

    def retrieve_doi(self, doi):
        response = None

        try:
            response = requests.get(
                '{}/dois/{}'.format(self.url, doi),
                headers=self.headers,
                auth=HTTPBasicAuth(self.username, self.password),
            )

            response.raise_for_status()

        except requests.exceptions.HTTPError as exception:
            pass

        return response

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

            created = True
        except requests.exceptions.HTTPError as exception:
            pass

        try:
            if response.status_code == 422:
                response = requests.put(
                    '{}/dois/{}'.format(self.url, doi),
                    data=data,
                    headers=self.headers,
                    auth=HTTPBasicAuth(self.username, self.password),
                )

                response.raise_for_status()

                updated = True
        except requests.exceptions.HTTPError as exception:
            pass

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
                headers=self.headers,
                auth=HTTPBasicAuth(self.username, self.password),
            )

            response.raise_for_status()

            deleted = True

        except requests.exceptions.HTTPError as exception:
            deleted = False

        return deleted, response
