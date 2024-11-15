#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json
import logging
from builtins import object
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from impala import conf

LOG = logging.getLogger()


@pytest.mark.django_db
class TestImpala(object):

  def setup_method(self):
    self.client = make_logged_in_client()

  def test_invalidate(self):
    with patch('impala.api.beeswax_dbms') as beeswax_dbms:
      invalidate = Mock()
      beeswax_dbms.get = Mock(
        return_value=Mock(invalidate=invalidate)
      )

      response = self.client.post(reverse("impala:invalidate"), {
          'flush_all': False,
          'cluster': json.dumps({"credentials": {}, "type": "direct", "id": "default", "name": "default"}),
          'database': 'default',
          'table': 'k8s_logs'
        }
      )

      assert invalidate.called

      assert response.status_code == 200
      content = json.loads(response.content)
      assert content['message'] == 'Successfully invalidated metadata'
