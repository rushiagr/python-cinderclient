# Copyright 2012 NetApp
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Interface for shares extention."""

from cinderclient.v1.contrib.shares_ext.manager import ShareManager
from cinderclient.v1.contrib.shares_ext.shell import (do_share_create,
                                                      do_share_delete,
                                                      do_share_show,
                                                      do_share_allow,
                                                      do_share_deny,
                                                      do_share_access_list,
                                                      do_share_list)
