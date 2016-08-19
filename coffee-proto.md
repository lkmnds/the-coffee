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

AUTH2 is optional. it stands for Authentication Number 2 and when it is called, all *messages* go encrypted, AES is recommended(TODO: user/password support)

#### Ask for supported algorithims
```
P: AUTH2 SHOW_ALGO
M: AES_256_DH [...]
```

#### Authenticating
Mc stands for an encrypted message from the Coffee Machine, Pc stands for the encrypted message from the programmer as well.

When authenticated, all communications between P and M *are* going to be encrypted as well(TODO: support against MITM attacks, nobody knows when you order a Hot Chocolate when it is making a Cappuccino)

```
P: AUTH2 LOGIN <sha512/bcrypt(password)> <SHA512/BCRYPT>
Mc: HAI
```

## Commands

### As usual, brew coffee
```
P: TARGET COFFEE
M: ST OK
```

### Or, if you want a hot chocolate
```
P: TARGET HOTCHOC
M: ST OK
```

### Scripting

(more documentation on that in [coffee-scripting.md](coffee-scripting.md))

```
P: TARGET SCRIPT
M: ST RECV
P: /x04echo Hello World/x05EXEC
M: ST EXEC
M: STDOUT "Hello World"
M: STDERR ""
```

#### Calculations and whatnot

```
...
[TARGET SCRIPT]
P: /x04mul 4,3/x05EXEC
M: ST EXEC
M: STDOUT "12"
M: STDERR ""
```

## Ask the Machine's status

```
P: ST NOW
```

### Possible statuses
```
M: ST <STATUS> <TASK_ID>
```

Example:
```
M: ST WAITING_TARGET 0
M: ST MAKING_COFFEE 21
M: ST MAKING_HOTCHOC 5
M: ST MAKING_SHIT 7
```

#### Check more about a status
```
P: ST QUERY <TASK_ID>
```

The machine sends JSON data about the status
```javascript
M: {
	"name": "MAKING_COFFEE", // str
	"id": 43, // int
	"target_time": <unix timestamp>, // int
	"owner": <user who sent TARGET to that>, // str
	}
```

## Stats

Servers can enable the STATS feature and clients can retrieve statistics from the server
```
P: STATS
```
```javascript
M: {
	"uptime": 10231, // uptime of server
	"target_queue": 4, // 4 tasks in queue
	"drinks": {
		'COFFEE': 21,
		'HOTCHOC': 3,
		...
	},
	...
}
```
