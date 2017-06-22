#!/usr/bin/env python

from cloudify import ctx


if __name__ == '__main__':

    ctx.instance.runtime_properties['node_instance_id'] = ctx.instance.id
