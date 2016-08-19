# The coffee protocol

All protocol examples use A as the coffee machine and P as the ~~lazy~~ programmer

## Handshake

### As a basic implementation:

```
P: HAI MACHINE;FEATURES
A: AUTH COFFEE HOTCHOC
P: ALLRIGHT
```

### All features enabled

```
P: HAI MACHINE;FEATURES
A: MULTI AUTH AUTH2 COFFEE HOTCHOC STATS <...>
P: ALLRIGHT
```

## Authentication

12345 as the password:
```
P: AUTH 12345/n
A: HAI/n
```

Errors:
```
A: AUTH_NOPE -- wrong password
A: AUTH_NOAUTH -- AUTH is disabled in this server
```

### The AUTH2 feature

AUTH2 is optional in any server. AUTH2 says that each password needs to be transmitted with an encryption scheme, AES is recommended:

#### Ask for supported algorithims
```
P: AUTH2 SHOW_ALGO
A: AES_256_DH
```

#### Sending password
```
P: AUTH2 PASSWORD <encrypted stuff>
A: HAI <session token, encrypted as well>
```

If logged, all communications between A and B **need** to be encrypted as well(to protect against MITM attacks, no one knows when someone is making a coffee when you want a hot chocolate)

```
P: [AUTH2 TOKEN <token> <...message...>] -- all encrypted
A: [response] -- still encrypted
```

## Commands

### As usual, brew coffee
```
P: TARGET COFFEE
A: ST OK
```

### Or, if you want a hot chocolate
```
P: TARGET HOTCHOCOLATE
A: ST OK
```

### You can send any script to the machine(more documentation on that later)
```
P: TARGET CUSTOM
A: SEND_ME
P: echo("hello");
P: \x04END_SCRIPT\x04
A: ST EXEC
A: RESULT "hello"
```

#### Calculations and whatnot

```
...
A: SEND_ME
P: echo(2+2*5);
P: ...end header...
A: ST EXEC
A: RESULT "12"
...
```

## Status

```
P: ST ?
A: ST MAKING_SHIT
```

## Stats

Servers can enable stats and clients can retrieve stats from the server, however, the STATS feature needs to be enabled in handshake
```
P: STATS
A: <JSON statistics>
```
