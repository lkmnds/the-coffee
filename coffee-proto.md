# The coffee protocol

All protocol examples use M as the coffee machine and P as the ~~lazy~~ programmer

## Handshake

### As a basic implementation:

```
P: HAI MACHINE;FEATURES
M: AUTH COFFEE HOTCHOC
P: ALLRIGHT
```

### All features available

```
P: HAI MACHINE;FEATURES
M: MULTI AUTH AUTH2 COFFEE HOTCHOC STATS <...>
P: ALLRIGHT
```

## Authentication

Authentication protects the Coffee Machine against snoopers or hackers, it compares the given password with the machine's password(TODO: implement user/password system)

12345 as the password:
```
P: AUTH 12345
M: HAI
```

Errors:
```
M: AUTH_NOPE -- wrong password
M: AUTH_NOAUTH -- AUTH is disabled in this server
```

### The AUTH2 feature

AUTH2 is optional in any server. AUTH2 says that each password needs to be transmitted with an encryption scheme, AES is recommended:

#### Ask for supported algorithims
```
P: AUTH2 SHOW_ALGO
M: AES_256_DH
```

#### Sending password
```
P: AUTH2 PASSWORD <encrypted stuff>
M: HAI <session token, encrypted as well>
```

If logged, all communications between A and B **need** to be encrypted as well(to protect against MITM attacks, no one knows when someone is making a coffee when you want a hot chocolate)

```
P: [AUTH2 TOKEN <token> <...message...>] -- all encrypted
M: [response] -- still encrypted
```

## Commands

### As usual, brew coffee
```
P: TARGET COFFEE
M: ST OK
```

### Or, if you want a hot chocolate
```
P: TARGET HOTCHOCOLATE
M: ST OK
```

### You can send any script to the machine(more documentation on that later)
```
P: TARGET CUSTOM
M: SEND_ME
P: echo("hello");
P: \x04END_SCRIPT\x04
M: ST EXEC
M: RESULT "hello"
```

#### Calculations and whatnot

```
...
M: SEND_ME
P: echo(2+2*5);
P: ...end header...
M: ST EXEC
M: RESULT "12"
...
```

## Status

```
P: ST ?
M: ST MAKING_SHIT
```

## Stats

Servers can enable stats and clients can retrieve stats from the server, however, the STATS feature needs to be enabled in handshake
```
P: STATS
M: <JSON statistics>
```
