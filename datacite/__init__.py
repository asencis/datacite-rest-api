# -*- coding: utf-8 -*-
#
# This file is part of asencis.
#
# Copyright (C) 2020 asencis.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.


"""Python wrapper for the DataCite RESTful API."""

from .client import DataciteRESTAPIClient
from .version import __version__

__all__ = ('DataciteRESTAPIClient', '__version__')
