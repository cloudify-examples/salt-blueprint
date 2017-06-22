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

    return output


if __name__ == '__main__':

    ctx.logger.info(
        'Verifying that Salt service is installed and running.')

    # Check if Salt is running
    salt_minion_running = False
    salt_master_running = False
    ps_output = execute_command('ps -ef', log_output=False)

    for line in ps_output.split('\n'):
        if '/usr/bin/salt-master' in line:
            salt_master_running = True
        if '/usr/bin/salt-minion' in line:
            salt_minion_running = True

    if salt_master_running:
        ctx.logger.info('Salt master service is running.')
    elif salt_minion_running:
        ctx.logger.info('Salt minion service is running.')
    else:
        raise RecoverableError('Salt is not yet running.')
