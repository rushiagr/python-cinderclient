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

import collections
import os
import re
import urllib

from cinderclient import base
from cinderclient import exceptions
from cinderclient import utils


class Share(base.Resource):
    """A share is an extra block level storage to the OpenStack instances."""
    def __repr__(self):
        return "<Share: %s>" % self.id

    def delete(self):
        """Delete this share."""
        self.manager.delete(self)

    def allow(self, access_type, access):
        """Allow access to a share."""
        self._validate_access(access_type, access)
        return self.manager.allow(self, access_type, access)

    def deny(self, id):
        """Deny access from IP to a share."""
        return self.manager.deny(self, id)

    def access_list(self):
        """Deny access from IP to a share."""
        return self.manager.access_list(self)

    def _validate_access(self, access_type, access):
        if access_type == 'ip':
            self._validate_ip_range(access)
        elif access_type == 'passwd':
            self._validate_username(access)
        else:
            raise exceptions.CommandError(
                'Only ip and passwd type are supported')

    @staticmethod
    def _validate_username(access):
        valid_useraname_re = '\w{4,32}'
        username = access
        if not re.match(valid_useraname_re, username):
            exc_str = _('Invalid user name. Must be alphanum 4-32 chars long')
            raise exceptions.CommandError(exc_str)

    @staticmethod
    def _validate_ip_range(ip_range):
        ip_range = ip_range.split('/')
        exc_str = ('Supported ip format examples:\n'
                   '\t10.0.0.2, 10.0.0.*, 10.0.0.0/24')
        if len(ip_range) > 2:
            raise exceptions.CommandError(exc_str)
        allow_asterisk = (len(ip_range) == 1)
        ip_range = ip_range[0].split('.')
        if len(ip_range) != 4:
            raise exceptions.CommandError(exc_str)
        for item in ip_range:
            try:
                if 0 <= int(item) <= 255:
                    continue
                raise ValueError()
            except ValueError:
                if not (allow_asterisk and item == '*'):
                    raise exceptions.CommandError(exc_str)


class ShareManager(base.ManagerWithFind):
    """Manage :class:`Share` resources."""
    resource_class = Share

    def create(self, share_proto, size, snapshot_id=None, name=None,
               description=None):
        """Create NAS.

        :param size: Size of NAS in GB
        :param snapshot_id: ID of the snapshot
        :param name: Name of the NAS
        :param description: Short description of a share
        :param share_type: Type of NAS (NFS or CIFS)
        :rtype: :class:`Share`
        """
        body = {'share': {'size': size,
                          'snapshot_id': snapshot_id,
                          'name': name,
                          'description': description,
                          'share_type': share_proto}}
        return self._create('/shares', body, 'share')

    def get(self, share_id):
        """Get a share.

        :param share_id: The ID of the share to delete.
        :rtype: :class:`Share`
        """
        return self._get("/shares/%s" % share_id, "share")

    def list(self, detailed=True, search_opts=None):
        """Get a list of all shares.

        :rtype: list of :class:`Share`
        """
        if search_opts:
            query_string = urllib.urlencode([(key, value)
                                             for (key, value)
                                             in search_opts.items()
                                             if value])
            if query_string:
                query_string = "?%s" % (query_string,)
        else:
            query_string = ''

        if detailed:
            path = "/shares/detail%s" % (query_string,)
        else:
            path = "/shares%s" % (query_string,)

        return self._list(path, 'shares')

    def delete(self, share):
        """Delete a share.

        :param share: The :class:`Share` to delete.
        """
        self._delete("/shares/%s" % base.getid(share))

    def allow(self, share, access_type, access):
        """Allow access from IP to a shares.

        :param share: The :class:`Share` to delete.
        :param access_type: string that represents access type ('ip','domain')
        :param access: string that represents access ('127.0.0.1')
        """
        return self._action('os-allow_access', share,
                            {'access_type': access_type,
                             'access_to': access})

    def deny(self, share, id):
        """Deny access from IP to a shares.

        :param share: The :class:`Share` to delete.
        :param ip: string that represents ip address
        """
        return self._action('os-deny_access', share, {'access_id': id})

    def access_list(self, share):
        """Get access list to the share."""
        access_list = self._action("os-access_list", share)[1]["access_list"]
        if access_list:
            t = collections.namedtuple('Access', access_list[0].keys())
            return [t(*value.values()) for value in access_list]
        else:
            return []

    def _action(self, action, share, info=None, **kwargs):
        """Perform a share 'action'."""
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/shares/%s/action' % base.getid(share)
        return self.api.client.post(url, body=body)


#########################


def _find_share(cs, share):
    """Get a share by ID."""
    return utils.find_resource(cs.shares, share)


def _print_share(cs, share):
    info = share._info.copy()
    info.pop('links')
    utils.print_dict(info)


@utils.arg(
    'share_protocol',
    metavar='<share_protocol>',
    type=str,
    help='Share type (NFS or CIFS)')
@utils.arg(
    'size',
    metavar='<size>',
    type=int,
    help='Share size in GB')
@utils.arg(
    '--snapshot-id',
    metavar='<snapshot-id>',
    help='Optional snapshot id to create the share from. (Default=None)',
    default=None)
@utils.arg(
    '--name',
    metavar='<name>',
    help='Optional share name. (Default=None)',
    default=None)
@utils.arg(
    '--description',
    metavar='<description>',
    help='Optional share description. (Default=None)',
    default=None)
@utils.service_type('volume')
def do_share_create(cs, args):
    """Creates new NAS storage (NFS or CIFS)."""
    share = cs.shares.create(args.share_protocol, args.size, args.snapshot_id,
                             args.name, args.description)
    _print_share(cs, share)


@utils.arg(
    'share',
    metavar='<share>',
    help='ID of the NAS to delete.')
@utils.service_type('volume')
def do_share_delete(cs, args):
    """Deletes NAS storage."""
    cs.shares.delete(args.share)


@utils.arg(
    'share',
    metavar='<share>',
    help='ID of the NAS share.')
@utils.service_type('volume')
def do_share_show(cs, args):
    """Show details about a NAS share."""
    share = _find_share(cs, args.share)
    _print_share(cs, share)


@utils.arg(
    'share',
    metavar='<share>',
    help='ID of the NAS share to modify.')
@utils.arg(
    'access_type',
    metavar='<access_type>',
    help='access rule type (only "ip" is supported).')
@utils.arg(
    'access_to',
    metavar='<access_to>',
    help='Value that defines access')
@utils.service_type('volume')
def do_share_allow(cs, args):
    """Allow access to the share."""
    share = _find_share(cs, args.share)
    share.allow(args.access_type, args.access_to)


@utils.arg(
    'share',
    metavar='<share>',
    help='ID of the NAS share to modify.')
@utils.arg(
    'id',
    metavar='<id>',
    help='id of the access rule to be deleted.')
@utils.service_type('volume')
def do_share_deny(cs, args):
    """Deny access to a share."""
    share = _find_share(cs, args.share)
    share.deny(args.id)


@utils.arg(
    'share',
    metavar='<share>',
    help='ID of the share.')
@utils.service_type('volume')
def do_share_access_list(cs, args):
    """Show access list for share."""
    share = _find_share(cs, args.share)
    access_list = share.access_list()
    utils.print_list(access_list, ['id', 'access type', 'access to', 'state'])


@utils.arg(
    '--all-tenants',
    dest='all_tenants',
    metavar='<0|1>',
    nargs='?',
    type=int,
    const=1,
    default=0,
    help='Display information from all tenants (Admin only).')
@utils.arg(
    '--name',
    metavar='<name>',
    default=None,
    help='Filter results by name')
@utils.arg(
    '--status',
    metavar='<status>',
    default=None,
    help='Filter results by status')
@utils.service_type('volume')
def do_share_list(cs, args):
    """List all NAS shares."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'name': args.name,
        'status': args.status,
    }
    shares = cs.shares.list(search_opts=search_opts)
    utils.print_list(shares,
                     ['ID', 'Name', 'Size', 'Share Type', 'Status',
                      'Export location'])
