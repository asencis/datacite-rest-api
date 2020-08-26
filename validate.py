# -*- coding: utf-8 -*-
#
# This file is part of asencis.
#
# Copyright (C) 2020 asencis.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.
import os
import json

from jsonschema import validate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def validate_doi_schema42(instance):
    jsonschema_42 = os.path.join(BASE_DIR, 'datacite/schemas/datacite-schema4.2.json')
    with open(jsonschema_42) as schema:
        schema = json.loads(schema.read())

    validate(instance=instance, schema=schema)

def validate_doi_schema43(instance):
    jsonschema_43 = os.path.join(BASE_DIR, 'datacite/schemas/datacite-schema4.3.json')
    with open(jsonschema_43) as schema:
        schema = json.loads(schema.read())

    validate(instance=instance, schema=schema)
