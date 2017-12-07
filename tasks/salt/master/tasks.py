import collections
from tempfile import NamedTemporaryFile
try:
    import yaml
except ImportError:
    import pip
    pip.main(['install', 'pyyaml'])
finally:
    from yaml import load, dump
    try:
        from yaml import CDumper as Dumper
    except ImportError:
        from yaml import Dumper

from fabric.api import put, sudo
from cloudify import ctx
from cloudify.exceptions import RecoverableError


def _convert_yaml(_config):

    def _convert(data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(_convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(_convert, data))
        else:
            return data

    return dump(_convert(_config), Dumper=Dumper)


def _write_configuration(config, config_path):
    config = _convert_yaml(config)
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(config)
    temp_file.close()
    put(temp_file.name, config_path, use_sudo=True)


def create():

    ctx.logger.info('Verifying that Salt is installed.')

    # Check if Salt is running
    salt_master_service = sudo('systemctl status salt-master.service')
    if salt_master_service.return_code == 0:
        ctx.logger.debug('Salt installed and running.')
    elif salt_master_service.return_code == 3:
        raise RecoverableError('Salt is installed, but is not running.')
    else:
        raise RecoverableError(
            'Salt is not installed and not running: {0}'.format(salt_master_service))


def preconfigure():
    ctx.logger.info('Retrieving Salt Master Finger.')
    master_finger_string = sudo('salt-key -F master | grep master.pub | awk "{{print $2}}"')
    master_finger = [line.split() for line in master_finger_string.splitlines() if 'master.pub' in line][0][1]
    ctx.logger.debug('master_finger: {0}'.format(master_finger))
    ctx.target.instance.runtime_properties['master_finger'] = master_finger


def configure(resource_config):
    ctx.logger.info('Configuring Salt.')
    if not ctx.node.properties.get('use_external_resource', False):
        for key, value in resource_config.items():
            if key == 'pillar_roots' or key == 'file_roots':
                roots = value
                for root, dirs in roots.items():
                    for dir in dirs:
                        sudo('mkdir -p {0}'.format(dir))

        _write_configuration(resource_config, '/etc/salt/master')
        sudo('systemctl restart salt-master.service')


def establish():
    minion = ctx.source.instance.runtime_properties.get('hostname')
    minion = minion.lstrip()
    minion = minion.rstrip()
    ctx.logger.info('Authorizing Minion: {0}.'.format(minion))
    sudo('salt-key -y -a {0}'.format(minion))
