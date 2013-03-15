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
"""Shell commands for shares."""

from cinderclient import utils


def _find_share(cs, share):
    """Get a share by ID."""
    return utils.find_resource(cs.shares, share)


def _print_share(cs, share):
    utils.print_dict(share._info)


@utils.arg('share_protocol',
           metavar='<share_protocol>',
           type=str,
           help='Share type (NFS or CIFS)')
@utils.arg('size',
           metavar='<size>',
           type=int,
           help='Share size in GB')
@utils.arg(
    '--snapshot_id',
    metavar='<snapshot_id>',
    help='Optional snapshot id to create the share from. (Default=None)',
    default=None)
@utils.arg('--display_name', metavar='<display_name>',
           help='Optional share name. (Default=None)',
           default=None)
@utils.arg('--display_description',
           metavar='<display_description>',
           help='Optional share description. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_share_create(cs, args):
    """Creates new NAS storage (NFS or CIFS)."""
    cs.shares.create(args.share_protocol, args.size, args.snapshot_id,
                     args.display_name, args.display_description)


@utils.arg('share', metavar='<share>', help='ID of the NAS to delete.')
@utils.service_type('volume')
def do_share_delete(cs, args):
    """Deletes NAS storage."""
    cs.shares.delete(args.share)


@utils.arg('share', metavar='<share>', help='ID of the NAS share.')
@utils.service_type('volume')
def do_share_show(cs, args):
    """Show details about a NAS share."""
    share = _find_share(cs, args.share)
    _print_share(cs, share)


@utils.arg('share', metavar='<share>', help='ID of the NAS share to modify.')
@utils.arg('access_type', metavar='<access_type>',
           help='access rule type (only "ip" is supported).')
@utils.arg('access_to', metavar='<access_to>',
           help='Value that defines access')
@utils.service_type('volume')
def do_share_allow(cs, args):
    """Allow access to the share."""
    share = _find_share(cs, args.share)
    share.allow(args.access_type, args.access_to)


@utils.arg('share', metavar='<share>', help='ID of the NAS share to modify.')
@utils.arg('id', metavar='<id>', help='id of the access rule to be deleted.')
@utils.service_type('volume')
def do_share_deny(cs, args):
    """Deny access to a share."""
    share = _find_share(cs, args.share)
    share.deny(args.id)


@utils.arg('share', metavar='<share>', help='ID of the share.')
@utils.service_type('volume')
def do_share_access_list(cs, args):
    """Show access list for share."""
    share = _find_share(cs, args.share)
    access_list = share.access_list()
    utils.print_list(access_list, ['id', 'access type', 'access to', 'state'])


@utils.service_type('volume')
def do_share_list(cs, args):
    """List all NAS shares."""
    shares = cs.shares.list()
    for share in shares:
        servers = share.export_location
        if (type(servers) is list):
            setattr(share, 'attached_to', ', '.join(servers))
        else:
            setattr(share, 'attached_to', share.export_location)
    utils.print_list(shares, ['ID', 'Display Name',
                     'Size', 'Share Type', 'Status', 'Export location'])
