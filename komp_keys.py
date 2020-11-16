#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script adds Key-Value Pairs to images in a Dataset with the specified name
for 50 users (user-1 through user-50). The Key-Value Pairs are defined in the
variables kvp_setx and are added to the images inside the dataset according to
the features in the images in the list images_kvp_order.
The script could be simplified by adding the Key-Value Pairs randomly to the
images in the Dataset.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from ezomero import get_group_id, get_map_annotation_ids, set_group, post_map_annotation, get_map_annotation
from getpass import getpass


def create_connection(server, port, sudo, user, group):
    if sudo:
        password = getpass('Enter password for user '+ sudo + ":")
        su_conn = BlitzGateway(sudo, password, host=server, port=port)
        su_conn.connect()
        conn = su_conn.suConn(user, group, 600000)
        su_conn.close()
    else:
        password = getpass('Enter password for user '+ user +":")
        conn = BlitzGateway(user, password, host=server, port=port)
        groupid = get_group_id(conn, group)
        set_group(conn, groupid)
        conn.connect()
    return conn

def create_annotations():
    ann = [{"fundus":"", "comments":"","annotation_status":""},
           {"cornea":"", "iris":"", "ciliary_body":"", "lens":"", "retina":"", "RPE":"", "choroid":"", "sclera":"", "optic_nerve_head":"", "comments":"", "annotation_status":""}]
    return ann

def find_images(conn, type, target):
    objs = conn.getObjects(type, attributes={'name': target})
    target_ids=[]
    if type == 'Image':
        target_ids = [d.getId() for d in objs]
        
    elif type == 'Dataset':
        for d in objs:
            for i in d.listChildren():
                target_ids.append(i.getId())
    elif type == 'Project':
        for p in objs:
            for d in p.listChildren():
                for i in d.listChildren():
                    target_ids.append(i.getId())

    return conn.getObjects('Image',target_ids)


def add_annotations(conn, images, ann):
    namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
    for (count, image) in enumerate(images):
        ann_ids = get_map_annotation_ids(conn, 'Image', image.getId(), ns=namespace)
        skip = False
        for a in ann_ids:
            dic = get_map_annotation(conn, a)
            if 'annotation_status' in dic.keys():
                print("Keys already created for image ", image.getName())
                skip = True
        if skip:
            continue
        else:
        
            if image.getName().endswith('.ndpi [0]'):                
                post_map_annotation(conn, 'Image', image.getId(), ann[1], namespace)
                print('linking to image', image.getName())
            elif image.getName().endswith('.tif'):
                post_map_annotation(conn, 'Image', image.getId(), ann[0], namespace)
                print('linking to image', image.getName())
          


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('target_type', type=str, help='Type of target to add keys to (project, dataset, image)')
    parser.add_argument('target', type=str, help='Target name to add keys to')
    parser.add_argument('--user',
                        type=str,
                        help='OMERO user that will own the annotation',
                        default='mpk')
    parser.add_argument('--groupid',
                        type=str,
                        help='OMERO group where target exists',
                        default='KOMP_eye')
    parser.add_argument('--sudo',
                        type=str,
                        required=False,
                        help='OMERO user for logging in (if sudoing to add annotations on behalf of someone else)')
    parser.add_argument('--server', default="bhomero01lp.jax.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    
    conn = create_connection(args.server, args.port, args.sudo, args.user, args.groupid)
    ann = create_annotations()
    images = find_images(conn, args.target_type, args.target)
    add_annotations(conn, images, ann)
    #run(args.password, args.target, args.server, args.port)
    conn.close()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
