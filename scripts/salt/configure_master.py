#!/usr/bin/env python

import subprocess
from os import system

from cloudify import ctx
from cloudify.exceptions import RecoverableError

MASTER_CONFIG_PATH = '/etc/salt/master'


def execute_command(_command):

    ctx.logger.debug('_command {0}.'.format(_command))

    subprocess_args = {
        'args': _command.split(),
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE
    }

    ctx.logger.debug('subprocess_args {0}.'.format(subprocess_args))

    process = subprocess.Popen(**subprocess_args)
    output, error = process.communicate()

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


if __name__ == '__main__':

    ctx.logger.debug('Checking if Salt Master is running.')

    # Check if Salt is running
    salt_running = False
    ps_output = execute_command('ps -ef')
    for line in ps_output.split('\n'):
        if '/usr/bin/salt-master' in line:
            salt_running = True
    if not salt_running:
        raise RecoverableError('Salt is not yet running.')

    ctx.logger.info('Salt is running.')
    if not ctx.node.properties.get('use_external_resource', False):
        ctx.logger.debug('Updating configuration file.')

        # Check if Salt is already configured
        configured = False
        ps_output = execute_command('sudo cat {0}'.format(MASTER_CONFIG_PATH))
        for line in ps_output.split('\n'):
            if line.startswith('interface:'):
                configured = True
                ctx.logger.debug('Salt already configured.')

        # Configure Salt
        if not configured:
            system('echo \"interface: {0}\" | sudo tee -a {1}'.format(ctx.instance.host_ip, MASTER_CONFIG_PATH))

        # Restart Salt Daemon
        ctx.logger.debug('Restarting Salt.')
        execute_command('sudo systemctl restart salt-master.service')

    # Log and Store the Salt Master Key Finger
    ctx.logger.debug('Getting Salt Master Key Finger')
    master_finger_string = execute_command('sudo salt-key -F master | grep master.pub | awk "{{print $2}}"')
    master_finger = [line.split() for line in master_finger_string.splitlines() if 'master.pub' in line][0][1]
    ctx.logger.debug('master_finger: {0}'.format(master_finger))
    ctx.instance.runtime_properties['master_finger'] = master_finger
