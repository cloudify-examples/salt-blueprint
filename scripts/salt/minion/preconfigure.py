#!/usr/bin/env python

import subprocess

from cloudify import ctx


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

    # Log and Store the Salt Master Key Finger
    ctx.logger.debug('Getting Salt Master Key Finger')
    master_finger_string = \
        execute_command(
            'sudo salt-key -F master | grep master.pub | awk "{{print $2}}"')
    master_finger = \
        [line.split() for line in master_finger_string.splitlines() if 'master.pub' in line][0][1]

    ctx.logger.debug('master_finger: {0}'.format(master_finger))
    ctx.target.instance.runtime_properties['master_finger'] = master_finger
