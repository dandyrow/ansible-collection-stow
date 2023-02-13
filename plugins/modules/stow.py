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
version_added: "1.0.0"
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


def main():
    # type: () -> None
    """runs Ansible stow module"""
    return


if __name__ == '__main__':
    main()
