#!/usr/bin/python

"""Ansible module to interact with GNU stow utility"""
# Copyright (C) 2023 Daniel Lowry <development@daniellowry.co.uk>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation under version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: stow
short_description: Module to interact with the GNU stow symbolic link manager.
version_added: "0.1.0"
author: Daniel Lowry (@dandyrow)
description: Module to interact with the GNU stow symbolic link manager.
options:
    src:
        description: The source path of the folders (packages) containing files to create symlinks for.
        required: true
        type: path
        aliases:
            - dir
    dest:
        description: The target path where the symlinks will be created.
        required: false
        type: path
        aliases:
            - target
    package:
        description: Name(s) of folders containing the files to be symlinked.
        required: True
        type: list
        elements: str
        aliases:
            - pkg
    state:
        description: Indicates the desired action for the module to carry out.
        type: str
        default: present
        choices:
            - present
            - absent
            - restow
    force:
        description: Whether to delete conflicting files in destination directory.
        type: bool
        default: No
'''


EXAMPLES = r'''
# Symlink zsh config files from dotfiles folder to home folder
- name: Stow zsh dotfiles into home
  dandyrow.stow.stow:
    src: ~/.dotfiles
    package: [ zsh ]

# Remove symlink of pacman config files from /etc
- name: Remove pacman config
  become: yes
  dandyrow.stow.stow:
    src: ~/.dotfiles
    dest: /etc/pacman.conf
    package:
      - pacman
    state: absent

# Force the deletion of any conflicting files when stowing
- name: Forcefully stow terminal configs
  dandyrow.stow.stow:
    src: ~/.dotfiles
    package:
        - zsh
        - neofetch
        - starship
    force: Yes

# Delete and re-stow git config
- name: Restow gitconfig
  dandyrow.stow.stow:
    src: ~/.dotfiles
    package: [ git ]
    state: restow
'''


RETURN = r''' # '''

# pylint: disable=wrong-import-position
import os

from collections import namedtuple
from ansible.module_utils.basic import AnsibleModule
# pylint: enable=wrong-import-position


State = {
    'present': '--stow',
    'absent': '--delete',
    'restow': '--restow'
}  # type: dict[str, str]


Params = namedtuple('Params', [
    'source_directory',
    'target_directory',
    'packages',
    'force',
    'stow_flag'
])


def init_module():
    # type: () -> AnsibleModule
    """Initiates an AnsibleModule with the argument spec"""
    return AnsibleModule(
        argument_spec=dict(
            src=dict(type='path', required=True, aliases=['dir']),
            dest=dict(type='path', aliases=['target']),
            package=dict(type='list', elements='str', required=True, aliases=['pkg']),
            force=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['present', 'absent', 'restow'])
        ),
        supports_check_mode=True
    )


def init_params(module_params):
    """Takes in module parameters handed in from Ansible and returns them in a namedtuple"""
    dest = module_params['dest']
    if dest is None:
        dest = os.path.dirname(module_params['src'])

    return Params(
        source_directory=module_params['src'],
        target_directory=dest,
        packages=module_params['package'],
        force=module_params['force'],
        stow_flag=State[module_params['state']]
    )


def validate_directories(directories, fail_func):
    """Call passed in function if any of the passed in directories don't exist.
    Function must take a message str as first argument"""
    err_msg = ''

    for directory in directories:
        if not os.path.isdir(directory):
            err_msg += 'Diretory \'{0}\' does not exist or is not a directory. '.format(directory)

    if err_msg != '':
        fail_func(err_msg)


def generate_stow_command(params, simulate=True):
    # type: (Params, bool) -> str
    """Returns a runnable stow command"""
    pkg_str = ' '.join(['{0} {1}'.format(params.stow_flag, package) for package in params.packages])

    if simulate:
        return 'stow --verbose --simulate --dir {0} --target {1} {2}'.format(
            params.source_directory, params.target_directory, pkg_str)

    return 'stow --verbose --dir {0} --target {1} {2}'.format(
        params.source_directory, params.target_directory, pkg_str)


def main():
    # type: () -> None
    """Runs Ansible stow module"""
    module = init_module()
    params = init_params(module.params)

    validate_directories([params.source_directory, params.target_directory], module.fail_json)

    cmd = generate_stow_command(params, True)
    return_code, stdout, stderr = module.run_command(cmd)

    if module.check_mode:
        module.exit_json()


if __name__ == '__main__':
    main()
