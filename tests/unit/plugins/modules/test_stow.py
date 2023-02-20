#!/usr/bin/env python

"""unit tests for Ansible stow module"""
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


# import unittest
import json

from unittest import TestCase, main
# from unittest.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.compat import typing
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.dandyrow.stow.plugins.modules import stow


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""


def set_module_args(args):
    # type: (dict[str, bool | str | typing.List[str]]) -> None
    """prepare arguments so that they will be picked up during module creation"""
    arg_str = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(arg_str)  # pylint: disable=protected-access


def exit_json(self, **kwargs):
    # type: (stow.AnsibleModule, typing.Any) -> typing.NoReturn
    """raises AnsibleExitJson. Mock exit_json method of AnsibleModule class for testing purposes"""
    raise AnsibleExitJson(kwargs)


# def fail_json(self, msg, **kwargs):  # pylint: disable=unused-argument
#     # type: (stow.AnsibleModule, typing.Any, typing.Any) -> typing.NoReturn
#     """raises AnsibleFailJson. Mock fail_json method of AnsibleModule class for testing purposes"""
#     kwargs['failed'] = True
#     kwargs['msg'] = msg
#     raise AnsibleFailJson(kwargs)


class TestModuleInit(TestCase):
    """Tests to ensure parameters are configured correctly in argument spec of Ansible Module"""

    def setUp(self):
        """Sets up mock functions for use during tests"""

        def fail_json(self, msg, **kwargs):  # pylint: disable=unused-argument
            """Raise AnsibleFailJson exception with kwargs"""
            kwargs['failed'] = True
            kwargs['msg'] = msg
            raise AnsibleFailJson(kwargs)

        stow.AnsibleModule.fail_json = fail_json

    def test_accepts_correct_parameters(self):
        """Tests the module accepts the parameters it should"""
        set_module_args(dict(
            src='/src/path',
            dest='/dest/path',
            package=['zsh', 'starship'],
            force=True,
            state='present'
        ))
        module = stow.init_module()
        self.assertIsInstance(module, stow.AnsibleModule)

    def test_accepts_aliased_parameters(self):
        """Tests the module accepts aliases of parameters which have them"""
        set_module_args(dict(
            dir='/src/path',
            target='/dest/path',
            pkg=['zsh', 'starship'],
            force=False,
            state='present'
        ))
        module = stow.init_module()
        self.assertIsInstance(module, stow.AnsibleModule)

    def test_parameters_type_correctly_set(self):
        """Tests types of parameters are set correctly in the module argument spec"""
        set_module_args(dict(
            src='/src/path',
            dest='/dest/path',
            package=['zsh', 'starship'],
            force=True,
            state='present'
        ))
        module = stow.init_module()
        # type ignore hints needed as AnsibleModule module is untyped
        self.assertIsInstance(module.params['src'], str)        # type: ignore
        self.assertIsInstance(module.params['dest'], str)       # type: ignore
        self.assertIsInstance(module.params['package'], list)   # type: ignore
        self.assertIsInstance(module.params['force'], bool)     # type: ignore
        self.assertIsInstance(module.params['state'], str)      # type: ignore

    def test_state_parameter_restricted_to_choices(self):
        """Tests state only accepts the allowed choices"""
        set_module_args(dict(
            src='/src/path',
            dest='/dest/path',
            package=['zsh', 'starship'],
            force=True,
            state='absent'
        ))
        module = stow.init_module()
        self.assertIsInstance(module, stow.AnsibleModule)

        set_module_args(dict(
            src='/src/path',
            dest='/dest/path',
            package=['zsh', 'starship'],
            force=True,
            state='restow'
        ))
        module = stow.init_module()
        self.assertIsInstance(module, stow.AnsibleModule)
        # no need to check present here as it is verified in other tests


class TestParamsInit(TestCase):
    """Tests the storage of module parameters into a namedtuple"""

    def test_params_creation(self):
        """Test creation of namedtuple with all parameters set"""
        mock_module_params = {
            'src': '/src/path',
            'dest': '/dest/path',
            'package': ['zsh', 'starship'],
            'force': True,
            'state': 'present'
        }
        expected_params = stow.Params(
            source_directory='/src/path',
            target_directory='/dest/path',
            packages=['zsh', 'starship'],
            force=True,
            stow_flag='--stow'
        )
        actual_params = stow.init_params(mock_module_params)
        self.assertTupleEqual(expected_params, actual_params)

    def test_creation_without_dest(self):
        """Test creation of namedtuple without destintation set"""
        mock_module_params = {
            'src': '/src/path',
            'dest': None,
            'package': ['zsh', 'starship'],
            'force': True,
            'state': 'present'
        }
        expected_params = stow.Params(
            source_directory='/src/path',
            target_directory='/src',
            packages=['zsh', 'starship'],
            force=True,
            stow_flag='--stow'
        )
        actual_params = stow.init_params(mock_module_params)
        self.assertTupleEqual(expected_params, actual_params)

    def test_other_stow_flags(self):
        """Test creation of namedtuple with other state values"""
        mock_module_params = {
            'src': '/src/path',
            'dest': '/dest/path',
            'package': ['zsh', 'starship'],
            'force': True,
            'state': 'absent'
        }
        expected_params = stow.Params(
            source_directory='/src/path',
            target_directory='/dest/path',
            packages=['zsh', 'starship'],
            force=True,
            stow_flag='--delete'
        )
        actual_params = stow.init_params(mock_module_params)
        self.assertTupleEqual(expected_params, actual_params)
        mock_module_params = {
            'src': '/src/path',
            'dest': '/dest/path',
            'package': ['zsh', 'starship'],
            'force': True,
            'state': 'restow'
        }
        expected_params = stow.Params(
            source_directory='/src/path',
            target_directory='/dest/path',
            packages=['zsh', 'starship'],
            force=True,
            stow_flag='--restow'
        )
        actual_params = stow.init_params(mock_module_params)
        self.assertTupleEqual(expected_params, actual_params)


class TestGenerateStowCmd(TestCase):
    """Tests function which generates stow command string"""

    def test_default_command_gen(self):
        """Test generation of stow command with simulate set to default (True)"""
        params = stow.Params(
            source_directory='/src',
            target_directory='/dest',
            packages=['zsh', 'neovim'],
            force=False,
            stow_flag='--stow'
        )
        expected_result = 'stow --verbose --simulate --dir /src --target /dest --stow zsh --stow neovim'
        actual_result = stow.generate_stow_command(params)
        self.assertEqual(expected_result, actual_result)

    def test_simulated_false(self):
        """Test generation of stow command with simulate set to false"""
        params = stow.Params(
            source_directory='/src',
            target_directory='/dest',
            packages=['zsh', 'neovim'],
            force=False,
            stow_flag='--stow'
        )
        expected_result = 'stow --verbose --dir /src --target /dest --stow zsh --stow neovim'
        actual_result = stow.generate_stow_command(params, False)
        self.assertEqual(expected_result, actual_result)


class TestDirValidation(TestCase):
    """Tests for stow directory validation function"""

    def isdir(self, path):
        # type: (str) -> bool
        """Return True if path is /this/path/exists otherwise return False"""
        return path == '/this/path/exists'

    def fail_json(self, msg, **kwargs):
        """Raise AnsibleFailJson exception with kwargs"""
        kwargs['failed'] = True
        kwargs['msg'] = msg
        raise AnsibleFailJson(kwargs)

    def test_calls_function_if_dir_not_exist(self):
        """Tests passed in function called if one of passed in directories doesn't exist"""
        stow.os.path.isdir = self.isdir

        with self.assertRaises(AnsibleFailJson):
            stow.validate_directories(['test', 'folder'], self.fail_json)

    def test_function_does_nothing_if_dir_exists(self):
        """Tests that nothing happens if all directories exist"""
        stow.os.path.isdir = self.isdir
        stow.validate_directories(['/this/path/exists'], self.fail_json)


class TestCommandResultParsing(TestCase):
    """Tests the command result parsing function"""

    def test_parses_values_to_dictionary(self):
        """Tests the command result parsing function works correctly"""
        return_code = 2
        stdout = 'this is standard out.\n'
        stderr = 'this is standard error.\nIt has an error.'

        result = stow.parse_command_result(return_code, stdout, stderr)

        self.assertEqual(result['rc'], 2)
        self.assertEqual(result['stdout'], 'this is standard out.\n')
        self.assertEqual(result['stdout_lines'], 'this is standard out.\n'.splitlines())
        self.assertEqual(result['stderr'], 'this is standard error.\nIt has an error.')
        self.assertEqual(result['stderr_lines'], 'this is standard error.\nIt has an error.'.splitlines())


if __name__ == '__main__':
    main()
