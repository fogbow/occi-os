# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
#    Copyright (c) 2012, Intel Performance Learning Solutions Ltd.
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


def create_storage(entity, context):
    """
    Create a storage instance.
    """
    size = float(entity.attributes['occi.storage.size'])

    # TODO(dizz): A blueprint?
    # OpenStack deals with size in terms of integer.
    # Need to convert float to integer for now and only if the float
    # can be losslessly converted to integer
    # e.g. See nova/quota.py:allowed_volumes(...)
    if not size.is_integer:
        msg = 'Volume sizes cannot be specified as fractional floats.'
        raise exc.HTTPBadRequest(msg)

    size = str(int(size))

    disp_name = ''
    try:
        disp_name = entity.attributes['occi.core.title']
    except KeyError:
        #Generate more suitable name as it's used for hostname
        #where no hostname is supplied.
        disp_name = entity.attributes['occi.core.title'] = str(random
        .randrange(0, 99999999)) + '-storage.occi-wg.org'
    if 'occi.core.summary' in entity.attributes:
        disp_descr = entity.attributes['occi.core.summary']
    else:
        disp_descr = disp_name

    snapshot = None
    # volume_type can be specified by mixin
    volume_type = None
    metadata = None
    avail_zone = None
    new_volume = volume_api.create(context,
                                   size,
                                   disp_name,
                                   disp_descr,
                                   snapshot=snapshot,
                                   volume_type=volume_type,
                                   metadata=metadata,
                                   availability_zone=avail_zone)
    return new_volume


def get_storage_instance(uid, context):
    """
    Retrieve a storage instance.
    """
    try:
        instance = volume_api.get(context, uid)
    except exception.NotFound:
        raise exc.HTTPNotFound()
    return instance


def delete_storage_instance(instance, context):
    """
    Delete a storage instance.
    """
    volume_api.delete(context, instance)


def snapshot_storage_instance(volume, name, description, context):
    """
    Snapshots an storage instance.
    """
    volume_api.create_snapshot(context, volume, name, description)


def get_image_architecture(instance, context):
    """
    Extract architecture from either:
    - image name, title or metadata. The architecture is sometimes
      encoded in the image's name
    - db::glance::image_properties could be used reliably so long as the
      information is supplied when registering an image with glance.
    - else return a default of x86
    """
    arch = ''
    id = instance['image_ref']
    img = image_api.show(context, id)
    img_properties = img['properties']
    if 'arch' in img_properties:
        arch = img['properties']['arch']
    elif 'architecture' in img_properties:
        arch = img['properties']['architecture']

    if arch == '':
        # if all attempts fail set it to a default value
        arch = 'x86'
    return arch