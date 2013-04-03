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

import os
import urllib

from cinderclient import base
from cinderclient import utils


class Snapshot(base.Resource):
    """Represent a snapshot of a share."""

    def __repr__(self):
        return "<Snapshot: %s>" % self.id

    def delete(self):
        """Delete this snapshot."""
        self.manager.delete(self)


class SnapshotManager(base.ManagerWithFind):
    """Manage :class:`Snapshot` resources.
    """
    resource_class = Snapshot

    def create(self, share_id, force=False, name=None, description=None):
        """Create a snapshot of the given share.

        :param share_id: The ID of the share to snapshot.
        :param force: If force is True, create a snapshot even if the
                      share is busy. Default is False.
        :param name: Name of the snapshot
        :param description: Description of the snapshot
        :rtype: :class:`Snapshot`
        """
        body = {'share-snapshot': {'share_id': share_id,
                                   'force': force,
                                   'name': name,
                                   'description': description}}
        return self._create('/share-snapshots', body, 'share-snapshot')

    def get(self, snapshot_id):
        """Get a snapshot.

        :param snapshot_id: The ID of the snapshot to get.
        :rtype: :class:`Snapshot`
        """
        return self._get('/share-snapshots/%s' % snapshot_id, 'share-snapshot')

    def list(self, detailed=True, search_opts=None):
        """Get a list of all snapshots of shares.

        :rtype: list of :class:`Snapshot`
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
            path = "/share-snapshots/detail%s" % (query_string,)
        else:
            path = "/share-snapshots%s" % (query_string,)

        return self._list(path, 'share-snapshots')

    def delete(self, snapshot):
        """Delete a snapshot of a share.

        :param share: The :class:`Snapshot` to delete.
        """
        self._delete("/share-snapshots/%s" % base.getid(snapshot))


#########################


def _find_share_snapshot(cs, snapshot):
    """Get a snapshot by ID."""
    return utils.find_resource(cs.share_snapshots, snapshot)


def _print_share_snapshot(cs, snapshot):
    info = snapshot._info.copy()
    info.pop('links')
    utils.print_dict(info)


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
@utils.arg(
    '--share-id',
    metavar='<share-id>',
    default=None,
    help='Filter results by share-id')
@utils.service_type('volume')
def do_share_snapshot_list(cs, args):
    """List all the snapshots."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'name': args.name,
        'status': args.status,
        'share_id': args.share_id,
    }
    snapshots = cs.share_snapshots.list(search_opts=search_opts)
    utils.print_list(snapshots,
                     ['ID', 'Share ID', 'Status', 'Name', 'Share Size'])


@utils.arg(
    'snapshot',
    metavar='<snapshot>',
    help='ID of the snapshot.')
@utils.service_type('volume')
def do_share_snapshot_show(cs, args):
    """Show details about a snapshot."""
    snapshot = _find_share_snapshot(cs, args.snapshot)
    _print_share_snapshot(cs, snapshot)


@utils.arg(
    'share_id',
    metavar='<share-id>',
    help='ID of the share to snapshot')
@utils.arg(
    '--force',
    metavar='<True|False>',
    help='Optional flag to indicate whether '
    'to snapshot a share even if it\'s busy.'
    ' (Default=False)',
    default=False)
@utils.arg(
    '--name',
    metavar='<name>',
    default=None,
    help='Optional snapshot name. (Default=None)')
@utils.arg(
    '--description',
    metavar='<description>',
    default=None,
    help='Optional snapshot description. (Default=None)')
@utils.service_type('volume')
def do_share_snapshot_create(cs, args):
    """Add a new snapshot."""
    snapshot = cs.share_snapshots.create(args.share_id,
                                         args.force,
                                         args.name,
                                         args.description)
    _print_share_snapshot(cs, snapshot)


@utils.arg(
    'snapshot_id',
    metavar='<snapshot-id>',
    help='ID of the snapshot to delete.')
@utils.service_type('volume')
def do_share_snapshot_delete(cs, args):
    """Remove a snapshot."""
    snapshot = _find_share_snapshot(cs, args.snapshot_id)
    snapshot.delete()
