# The coffee protocol

All protocol examples use A as the coffee machine and P as the ~~lazy~~ programmer

## Handshake

### As a basic implementation:

```
P: HAI MACHINE;FEATURES\n
A: AUTH COFFEE HOTCHOC\n
P: ALLRIGHT\n
```

### All features enabled

```
P: HAI MACHINE;FEATURES\n
A: MULTI AUTH AUTH2 COFFEE HOTCHOC STATS <...>\n
P: ALLRIGHT\n
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
P: AUTH2 SHOW_ALGO\n
A: AES_256_DH\n
```

#### Sending password
```
P: AUTH2 PASSWORD <encrypted stuff>\n
A: HAI <session token, encrypted as well>\n
```

If logged, all communications between A and B **need** to be encrypted as well(to protect against MITM attacks, no one knows when someone is making a coffee when you want a hot chocolate)

```
P: [AUTH2 TOKEN <token> <...message...>] -- all encrypted
A: [response] -- still encrypted
```

## Commands

### As usual, brew coffee
```
P: TARGET COFFEE\n
A: ST OK\n
```

### Or, if you want a hot chocolate
```
P: TARGET HOTCHOCOLATE\n
A: ST OK\n
```

### You can send any script to the machine(more documentation on that later)
```
P: TARGET CUSTOM\n
A: SEND_ME\n
P: echo("hello");
P: \x04END_SCRIPT\x04
A: ST EXEC\n
A: RESULT "hello"\n
```

#### Calculations and whatnot

```
...
A: SEND_ME\n
P: echo(2+2*5);
P: ...end header...
A: ST EXEC\n
A: RESULT "12"\n
...
```

## Status

```
P: ST ?\n
A: ST MAKING_SHIT\n
```

## Stats

Servers can enable stats and clients can retrieve stats from the server, however, the STATS feature needs to be enabled in handshake
```
P: STATS\n
A: <JSON statistics>\n
```
