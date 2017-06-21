#!/usr/bin/env python

import subprocess
from os import system

from cloudify import ctx
from cloudify.exceptions import RecoverableError
from cloudify.state import ctx_parameters as inputs

MINION_CONFIG_PATH = '/etc/salt/minion'


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

    ctx.logger.debug('Checking if Salt Minion is running.')

    # Check if Salt is running
    salt_running = False
    ps_output = execute_command('ps -ef')
    for line in ps_output.split('\n'):
        if '/usr/bin/salt-minion' in line:
            salt_running = True
    if not salt_running:
        raise RecoverableError('Salt is not yet running.')
    ctx.logger.debug('Salt is running. Updating configuration file.')

    # Check if Salt is already configured
    configured = False
    ps_output = execute_command('sudo cat {0}'.format(MINION_CONFIG_PATH))
    for line in ps_output.split('\n'):
        if line.startswith('master:'):
            configured = True
            ctx.logger.debug('Salt already configured.')

    # Configure Salt
    if not configured:
        interface = inputs['interface']
        system('echo \"master: {0}\" | sudo tee -a {1}'.format(interface, MINION_CONFIG_PATH))

        master_finger = inputs['master_finger']
        system('echo \"master_finger: \'{0}\'\" | sudo tee -a {1}'.format(master_finger, MINION_CONFIG_PATH))

    # Restart Salt Daemon
    ctx.logger.debug('Restarting Salt.')
    execute_command('sudo systemctl restart salt-minion.service')

    # Log the Salt Finger
    execute_command('sudo salt-call --local key.finger')
