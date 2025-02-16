#!/usr/bin/env python3
# Copyright 2023 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""Launch a pw_target_runner server to use for multi-device testing."""

import argparse
import logging
import sys
import tempfile
from typing import IO, List, Optional

import pw_cli.process
import pw_cli.log

try:
    from rp2040_utils import device_detector
except ImportError:
    # Load from this directory if rp2040_utils is not available.
    import device_detector  # type: ignore

_LOG = logging.getLogger('unit_test_server')

DEFAULT_PORT = 34172

_TEST_RUNNER_COMMAND = 'rp2040_unit_test_runner'
_TEST_SERVER_COMMAND = 'pw_target_runner_server'


def parse_args():
    """Parses command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--server-port',
        type=int,
        default=DEFAULT_PORT,
        help='Port to launch the pw_target_runner_server on',
    )
    parser.add_argument(
        '--server-config',
        type=argparse.FileType('r'),
        help='Path to server config file',
    )
    parser.add_argument(
        '--verbose',
        '-v',
        dest='verbose',
        action="store_true",
        help='Output additional logs as the script runs',
    )

    return parser.parse_args()


def generate_runner(command: str, arguments: List[str]) -> str:
    """Generates a text-proto style pw_target_runner_server configuration."""
    # TODO(amontanez): Use a real proto library to generate this when we have
    # one set up.
    for i, arg in enumerate(arguments):
        arguments[i] = f'  args: "{arg}"'
    runner = ['runner {', f'  command:"{command}"']
    runner.extend(arguments)
    runner.append('}\n')
    return '\n'.join(runner)


def generate_server_config() -> IO[bytes]:
    """Returns a temporary generated file for use as the server config."""
    boards = device_detector.detect_boards()
    if not boards:
        _LOG.critical('No attached boards detected')
        sys.exit(1)
    config_file = tempfile.NamedTemporaryFile()
    _LOG.debug('Generating test server config at %s', config_file.name)
    _LOG.debug('Found %d attached devices', len(boards))

    # TODO: b/290245354 - Multi-device flashing doesn't work due to limitations
    # of picotool. Limit to one device even if multiple are connected.
    if boards:
        boards = boards[:1]

    for board in boards:
        test_runner_args = [
            '--usb-bus',
            str(board.bus),
            '--usb-port',
            str(board.port),
            '--serial-port',
            board.serial_port,
        ]
        config_file.write(
            generate_runner(_TEST_RUNNER_COMMAND, test_runner_args).encode(
                'utf-8'
            )
        )
    config_file.flush()
    return config_file


def launch_server(
    server_config: Optional[IO[bytes]], server_port: Optional[int]
) -> int:
    """Launch a device test server with the provided arguments."""
    if server_config is None:
        # Auto-detect attached boards if no config is provided.
        server_config = generate_server_config()

    cmd = [_TEST_SERVER_COMMAND, '-config', server_config.name]

    if server_port is not None:
        cmd.extend(['-port', str(server_port)])

    return pw_cli.process.run(*cmd, log_output=True).returncode


def main():
    """Launch a device test server with the provided arguments."""
    args = parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    pw_cli.log.install(level=log_level)

    exit_code = launch_server(args.server_config, args.server_port)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
