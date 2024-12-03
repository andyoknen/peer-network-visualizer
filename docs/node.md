Node RPC API Reference

## `getnodeinfo`

Request:

```bash
curl --location 'http://1.pocketnet.app:38081/rpc/public/' \
--header 'Content-Type: application/json' \
--data '{
    "method": "getnodeinfo",
    "params": []
}'
```

Answer:

```json
{
    "result": {
        "version": "0.22.8",
        "time": 1733147762,
        "chain": "main",
        "proxy": true,
        "netstakeweight": 366169806977158,
        "lastblock": {
            "height": 3050710,
            "hash": "32c3b8b5fb4db7df9cef1c6dca125a41b9f21b96fb8e74d90c5c1e8b91e16e67",
            "time": 1733147760,
            "ntx": 76
        },
        "proxies": [],
        "ports": {
            "node": 37070,
            "api": 38081,
            "rest": 38083,
            "wss": 8087,
            "http": 38082,
            "https": 38082
        }
    },
    "error": null,
    "id": null
}
```

## `getpeerinfo`

Request:

```bash
curl --location 'http://1.pocketnet.app:38081/rpc/public/' \
--header 'Content-Type: application/json' \
--data '{
    "method": "getpeerinfo",
    "params": []
}'
```

Answer:

```json
{
    "result": [
        {
            "addr": "178.168.110.85:51044",
            "services": "0000000000000409",
            "relaytxes": true,
            "lastsend": 1733148007,
            "lastrecv": 1733148008,
            "conntime": 1732844055,
            "timeoffset": 0,
            "pingtime": 354114,
            "protocol": 70016,
            "version": "/Satoshi:0.22.7/",
            "inbound": false,
            "startingheight": 3045622,
            "whitelisted": false,
            "banscore": 0,
            "synced_headers": 3050709,
            "synced_blocks": 3050709
        },
        {
            "addr": "195.222.85.245:49709",
            "services": "0000000000000409",
            "relaytxes": false,
            "lastsend": 1733148007,
            "lastrecv": 1733148008,
            "conntime": 1732844075,
            "timeoffset": 0,
            "pingtime": 43915,
            "protocol": 70016,
            "version": "/Satoshi:0.22.8/",
            "inbound": true,
            "startingheight": 3045622,
            "whitelisted": true,
            "banscore": 0,
            "synced_headers": 3050710,
            "synced_blocks": 3050710
        },
        ...
    ],
    "error": null,
    "id": null
}
```