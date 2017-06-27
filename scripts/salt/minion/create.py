#!/usr/bin/env python

import subprocess

from cloudify import ctx
from cloudify.exceptions import RecoverableError


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

    return process, output


if __name__ == '__main__':

    ctx.logger.info(
        'Verifying that Salt service is installed and running.')

    # Check if Salt is running
    salt_running = False
    salt_minion_service, command_output = \
        execute_command('sudo systemctl status salt-minion.service', log_output=False)

    if salt_minion_service.returncode == 0 and command_output != -1:
        ctx.logger.debug('Salt installed and running.')
    elif salt_minion_service.returncode == 3:
        raise RecoverableError('Salt is installed, but is not running.')
    else:
        raise RecoverableError(
            'Salt is not installed and not running: {0}'.format(command_output))
