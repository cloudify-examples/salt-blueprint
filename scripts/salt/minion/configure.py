#!/usr/bin/env python

import collections
import subprocess
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

from cloudify import ctx
from cloudify.state import ctx_parameters as inputs

MINION_CONFIG_PATH = '/etc/salt/minion'


def execute_command(_command, log_output=True):

    ctx.logger.debug('_command {0}.'.format(_command))

    subprocess_args = {
        'args': _command.split(),
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE
    }

    ctx.logger.debug('subprocess_args {0}.'.format(subprocess_args))

    process = subprocess.Popen(**subprocess_args)
    output, error = process.communicate()

    if log_output:
        ctx.logger.debug(
            'command: {0} '.format(_command))
        ctx.logger.debug(
            'output: {0} '.format(output))
        ctx.logger.debug(
            'error: {0} '.format(error))
        ctx.logger.debug(
            'process.returncode: {0} '.format(process.returncode))

    if process.returncode:
        ctx.logger.error('Running `{0}` returns error.'.format(_command))
        return False

    return output


def convert_yaml(_config):

    def convert(data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data

    return dump(convert(_config), Dumper=Dumper)


def write_configuration(config, config_path):
    config = convert_yaml(config)
    ctx.logger.debug('type: {0}'.format(type(config)))
    ctx.logger.debug('Writing Salt configuration: {0}'.format(config))
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(config)
    temp_file.close()
    execute_command('sudo mv {0} {1}'.format(temp_file.name, config_path))


if __name__ == '__main__':

    salt_config = inputs.get('resource_config', {})
    write_configuration(salt_config, MINION_CONFIG_PATH)

    # Restart Salt Daemon
    ctx.logger.debug('Restarting Salt.')
    execute_command('sudo systemctl restart salt-minion.service')

    # Log the Salt Finger
    execute_command('sudo salt-call --local key.finger')
