# The coffee protocol

All protocol examples use A as the coffee machine and B as the ~~lazy~~ programmer

## Handshake

### As a basic implementation:

```
B: HAI MACHINE; FEATURES\n
A: AUTH COFFEE HOTCHOC\n
B: ALLRIGHT\n
```

### All features enabled

```
B: HAI MACHINE; FEATURES\n
A: MULTI AUTH AUTH2 COFFEE HOTCHOC STATS <...>\n
B: ALLRIGHT\n
```

## Authentication

12345 as the password:
```
B: AUTH 12345/n
A: HAI/n
```

Errors:
```
A: NOPE\n -- wrong password
A: NONO\n -- maximum amount of users already
```

### The AUTH2 feature

AUTH2 is optional in any server. AUTH2 says that each password needs to be transmitted with an encryption scheme, AES is recommended:

#### Ask for supported algorithims
```
B: AUTH2 SHOW_ALGO\n
A: AES_256_DH\n
```

#### Sending password
```
B: AUTH2 PASSWORD <encrypted stuff>\n
A: HAI <session token, encrypted as well>\n
```

If logged, all communications between A and B **need** to be encrypted as well(to protect against MITM attacks, no one knows when someone is making a coffee when you want a hot chocolate)

```
B: [AUTH2 TOKEN <token> <...message...>] -- all encrypted
A: [response] -- still encrypted
```

## Commands

### As usual, brew coffee
```
B: TARGET COFFEE\n
A: ST OK\n
```

### Or, if you want a hot chocolate
```
B: TARGET HOTCHOCOLATE\n
A: ST OK\n
```

### You can send any script to the machine(more documentation on that later)
```
B: TARGET CUSTOM\n
A: SEND_ME\n
B: echo("hello");
B: \x04END_SCRIPT\x04
A: ST EXEC\n
A: RESULT "hello"\n
```

#### Calculations and whatnot

```
...
A: SEND_ME\n
B: echo(2+2*5);
B: ...end header...
A: ST EXEC\n
A: RESULT "12"\n
...
```

## Status

```
B: ST ?\n
A: ST MAKING_SHIT\n
```

## Stats

Servers can enable stats and clients can retrieve stats from the server, however, the STATS feature needs to be enabled in handshake
```
B: STATS\n
A: <JSON statistics>\n
```

