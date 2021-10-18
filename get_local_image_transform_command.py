#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020–2021 CEA
#
# Author: Joël Chavas <joel.chavas@cea.fr>
#
# Licensed under the Apache Licence, Version 2.0 (the "Licence");
# you may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and
# limitations under the Licence.

import argparse
import shlex
import subprocess
import sys

import requests


"""
Source and target spaces can be one of the 4 spaces:
"MNI 152 ICBM 2009c Nonlinear Asymmetric"
"MNI Colin 27"
"Big Brain (Histology)"
"Infant Atlas"
"""
SOURCE_SPACE_DEFAULT = "MNI 152 ICBM 2009c Nonlinear Asymmetric"
TARGET_SPACE_DEFAULT = "Big Brain (Histology)"

SERVER_ADDRESS_DEFAULT = "https://hbp-spatial-backend.apps.hbp.eu"
# SERVER_ADDRESS_DEFAULT = "http://0.0.0.0:8080"
# SERVER_ADDRESS_DEFAULT = "http://172.17.0.1:8080"
INSTANCE_PATH = "/instance"


def is_transform(str_in):
    """Determines if str_in is the name of a transformation file
    """
    return '.ima' in str_in \
        or '.trm' in str_in


def add_path_to_transform(str_in):
    """Adds as prefix INSTANCE_PATH to str_in if str_in is a transformaton file
    """
    if is_transform(str_in):
        return f'{INSTANCE_PATH}/{str_in}'
    else:
        return str_in


def get_command(server_address, source_space, target_space):
    """Gets the image transform commmand from the server
    """
    request_string = \
        f'{server_address}/v1/'\
        f'get-image-transform-command?source_space={source_space}'\
        f'&target_space={target_space}&input_coords=auto'
    response = requests.get(request_string)
    response.raise_for_status()
    return response.json()['transform_command']


def format_command(command_from_server, input_file, output_file, extra):
    """Formats the command to a string that can be run on a bash shell

    Args:
        command_from_server: list
        input_file: string
        output_file: string
        extra: string
    """

    command_as_list = command_from_server

    # We construct command as a list
    command_as_list = [add_path_to_transform(x) for x in command_as_list]
    command_as_list += ['-i', input_file]
    command_as_list += ['-o', output_file]
    command_as_list += extra

    # We check that the first argument is 'AimsApplyTransform'
    if command_as_list[0] != 'AimsApplyTransform':
        raise ValueError("First argument is NOT \'AimsApplyTransform\', "
                         "which is NOT expected. "
                         f"Instead, it was \'{command_as_list[0]}\'. "
                         "For safety reason, this is forbidden.")

    return command_as_list


def parse_args(argv):
    """Function parsing command-line arguments

    Args:
        argv: a list containing command line arguments

    Returns:
        args: arguments used by this program
        extra: extra arguments passed to AimsApplyTransform
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='get_local_image_transform_command.py',
        description='Gets command to transform image among templates')
    parser.add_argument(
        "-a", "--server_address", type=str, default=SERVER_ADDRESS_DEFAULT,
        help='Server address from which to get the transform command. '
             'From inside docker, it is http://localhost:8080 .'
             'From outside docker, it is http://your_docker_ip:8080 .'
             'Or : https://hbp-spatial-backend.apps.hbp.eu .'
             'Default is : ' + SERVER_ADDRESS_DEFAULT)
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help='Path to input file name')
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help='Path to output file name')
    parser.add_argument(
        "-s", "--source_space", type=str, default=SOURCE_SPACE_DEFAULT,
        choices=["MNI 152 ICBM 2009c Nonlinear Asymmetric",
                 "MNI Colin 27",
                 "Big Brain (Histology)",
                 "Infant Atlas"],
        help='Source template space from which we make the transform '
             'Default is : ' + SOURCE_SPACE_DEFAULT)
    parser.add_argument(
        "-t", "--target_space", type=str, default=TARGET_SPACE_DEFAULT,
        choices=["MNI 152 ICBM 2009c Nonlinear Asymmetric",
                 "MNI Colin 27",
                 "Big Brain (Histology)",
                 "Infant Atlas"],
        help='Target template space to which we make the transform '
             'Default is : ' + TARGET_SPACE_DEFAULT)

    args, extra = parser.parse_known_args(argv)

    return args, extra


def main(argv):
    """Reads argument line and creates command line"""

    args, extra = parse_args(argv)
    command_from_server = get_command(
                            server_address=args.server_address,
                            source_space=args.source_space,
                            target_space=args.target_space)
    command_ready = format_command(
                            command_from_server=command_from_server,
                            input_file=args.input,
                            output_file=args.output,
                            extra=extra)

    # Print the AimsApplyTransform command on stdout
    print(' '.join(shlex.quote(arg) for arg in command_ready))

    # Executes command_ready directly as a system call
    retcode = subprocess.call(command_ready)

    return retcode


######################################################################
# Main program
######################################################################

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
