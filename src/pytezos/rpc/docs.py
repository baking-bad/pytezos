rpc_docs = {
  "/": {
    "props": [
      "chains",
      "config",
      "errors",
      "fetch_protocol",
      "health",
      "injection",
      "monitor",
      "network",
      "private",
      "profiler",
      "protocols",
      "stats",
      "version",
      "workers"
    ]
  },
  "/chains": {
    "item": {
      "name": "chain_id",
      "descr": "A chain identifier. This is either a chain hash in Base58Check notation or a one the predefined aliases: 'main', 'test'."
    }
  },
  "/chains/{}": {
    "PATCH": {
      "descr": "Forcefully set the bootstrapped flag of the node",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "active_peers_heads",
      "blocks",
      "chain_id",
      "delegators_contribution",
      "invalid_blocks",
      "is_bootstrapped",
      "levels",
      "mempool",
      "protocols"
    ]
  },
  "/chains/{}/active_peers_heads": {
    "GET": {
      "descr": "The heads of all active peers",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks": {
    "GET": {
      "descr": "Lists block hashes from '<chain>', up to the last checkpoint, sorted with decreasing fitness. Without arguments it returns the head of the chain. Optional arguments allow to return the list of predecessors of a given block or of a set of blocks.",
      "args": [
        {
          "name": "length",
          "descr": "The requested number of predecessors to return (per request; see next argument)."
        },
        {
          "name": "head",
          "descr": "An empty argument requests blocks starting with the current head. A non empty list allows to request one or more specific fragments of the chain."
        },
        {
          "name": "min_date",
          "descr": "When `min_date` is provided, blocks with a timestamp before `min_date` are filtered out. However, if the `length` parameter is also provided, then up to that number of predecessors will be returned regardless of their date."
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_id",
      "descr": "A block identifier. This can take one of the following values:\n\t1.Block-hash - Hash in Base58Check notation.\n\t2.Alias - One of the following:'genesis/ head/ caboose/ savepoint/ checkpoint'.\n\t3.Block-level - index(integer) in the chain.\n\tOne can also specify the relative positions of block with respect to above three block identifiers. For ex. 'checkpoint~N' or checkpoint+N, where N is an integer, denotes the Nth block before(~) or after (+) the checkpoint."
    }
  },
  "/chains/{}/chain_id": {
    "GET": {
      "descr": "The chain unique identifier.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/delegators_contribution": {
    "item": {
      "name": "int32",
      "descr": "\u00af\\_(\u30c4)_/\u00af"
    }
  },
  "/chains/{}/delegators_contribution/{}": {
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/delegators_contribution/{}/{}": {
    "GET": {
      "descr": "A breakdown of all the contributions to the delegation portion of the baking power of the given delegate for the given cycle.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/invalid_blocks": {
    "GET": {
      "descr": "Lists blocks that have been declared invalid along with the errors that led to them being declared invalid.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "block_hash",
      "descr": "block_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/invalid_blocks/{}": {
    "GET": {
      "descr": "The errors that appears during the block (in)validation.",
      "args": [],
      "ret": "Object"
    },
    "DELETE": {
      "descr": "Remove an invalid block for the tezos storage",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/is_bootstrapped": {
    "GET": {
      "descr": "The bootstrap status of a chain",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/levels": {
    "props": [
      "caboose",
      "checkpoint",
      "savepoint"
    ]
  },
  "/chains/{}/levels/caboose": {
    "GET": {
      "descr": "The current caboose for this chain.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/levels/checkpoint": {
    "GET": {
      "descr": "The current checkpoint for this chain.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/levels/savepoint": {
    "GET": {
      "descr": "The current savepoint for this chain.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/protocols": {
    "GET": {
      "descr": "Lists protocols of the chain.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "Protocol_hash",
      "descr": "Protocol_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/protocols/{}": {
    "GET": {
      "descr": "Information about a protocol of the chain.",
      "args": [],
      "ret": "Object"
    }
  },
  "/config": {
    "GET": {
      "descr": "Return the runtime node configuration (this takes into account the command-line arguments and the on-disk configuration file)",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "history_mode",
      "logging",
      "network"
    ]
  },
  "/config/history_mode": {
    "GET": {
      "descr": "Returns the history mode of the node's underlying storage. In full or rolling mode, it provides the values of `additional_cycles` and `blocks_preservation_cycles`. The sum of these values is the total number of stored cycles.",
      "args": [],
      "ret": "Object"
    }
  },
  "/config/logging": {
    "PUT": {
      "descr": "Replace the logging configuration of the node.",
      "args": [],
      "ret": "Object"
    }
  },
  "/config/network": {
    "props": [
      "dal",
      "user_activated_protocol_overrides",
      "user_activated_upgrades"
    ]
  },
  "/config/network/dal": {
    "GET": {
      "descr": "Configuration for the DAL",
      "args": [],
      "ret": "Object"
    }
  },
  "/config/network/user_activated_protocol_overrides": {
    "GET": {
      "descr": "List of protocols which replace other protocols",
      "args": [],
      "ret": "Array"
    }
  },
  "/config/network/user_activated_upgrades": {
    "GET": {
      "descr": "List of protocols to switch to at given levels",
      "args": [],
      "ret": "Array"
    }
  },
  "/errors": {
    "GET": {
      "descr": "Schema for all the RPC errors from the shell",
      "args": [],
      "ret": "Object"
    }
  },
  "/fetch_protocol": {
    "item": {
      "name": "Protocol_hash",
      "descr": "Protocol_hash (Base58Check-encoded)"
    }
  },
  "/fetch_protocol/{}": {
    "GET": {
      "descr": "Fetch a protocol from the network.",
      "args": [],
      "ret": "Object"
    }
  },
  "/health": {
    "props": [
      "ready"
    ]
  },
  "/health/ready": {
    "GET": {
      "descr": "Returns whether or not the node is ready to answer to requests.",
      "args": [],
      "ret": "Object"
    }
  },
  "/injection": {
    "props": [
      "block",
      "operation",
      "protocol"
    ]
  },
  "/injection/block": {
    "POST": {
      "descr": "Inject a block in the node and broadcast it. The `operations` embedded in `blockHeader` might be pre-validated using a contextual RPCs from the latest block (e.g. '/blocks/head/context/preapply'). Returns the ID of the block. By default, the RPC will wait for the block to be validated before answering. If ?async is true, the function returns immediately. Otherwise, the block will be validated before the result is returned. If ?force is true, it will be injected even on non strictly increasing fitness. An optional ?chain parameter can be used to specify whether to inject on the test chain or the main chain.",
      "args": [
        {
          "name": "async",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/injection/operation": {
    "POST": {
      "descr": "Inject an operation in node and broadcast it. Returns the ID of the operation. The `signedOperationContents` should be constructed using contextual RPCs from the latest block and signed by the client. The injection of the operation will apply it on the current mempool context. This context may change at each operation injection or operation reception from peers. By default, the RPC will wait for the operation to be (pre-)validated before returning. However, if ?async is true, the function returns immediately. The optional ?chain parameter can be used to specify whether to inject on the test chain or the main chain.",
      "args": [
        {
          "name": "async",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/injection/protocol": {
    "POST": {
      "descr": "Inject a protocol in node. Returns the ID of the protocol. If ?async is true, the function returns immediately. Otherwise, the protocol will be validated before the result is returned.",
      "args": [
        {
          "name": "async",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/monitor": {
    "props": [
      "active_chains",
      "applied_blocks",
      "bootstrapped",
      "heads",
      "protocols",
      "received_blocks",
      "validated_blocks"
    ]
  },
  "/monitor/active_chains": {
    "GET": {
      "descr": "Monitor every chain creation and destruction. Currently active chains will be given as first elements",
      "args": [],
      "ret": "Array"
    }
  },
  "/monitor/applied_blocks": {
    "GET": {
      "descr": "Monitor all blocks that are successfully applied and stored by the node, disregarding whether they were selected as the new head or not.",
      "args": [
        {
          "name": "protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "next_protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/monitor/bootstrapped": {
    "GET": {
      "descr": "Wait for the node to have synchronized its chain with a few peers (configured by the node's administrator), streaming head updates that happen during the bootstrapping process, and closing the stream at the end. If the node was already bootstrapped, returns the current head immediately.",
      "args": [],
      "ret": "Object"
    }
  },
  "/monitor/heads": {
    "item": {
      "name": "chain_id",
      "descr": "A chain identifier. This is either a chain hash in Base58Check notation or a one the predefined aliases: 'main', 'test'."
    }
  },
  "/monitor/heads/{}": {
    "GET": {
      "descr": "Monitor all blocks that are successfully validated and applied by the node and selected as the new head of the given chain.",
      "args": [
        {
          "name": "protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "next_protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/monitor/protocols": {
    "GET": {
      "descr": "Monitor all economic protocols that are retrieved and successfully loaded and compiled by the node.",
      "args": [],
      "ret": "Object"
    }
  },
  "/monitor/received_blocks": {
    "item": {
      "name": "chain_id",
      "descr": "A chain identifier. This is either a chain hash in Base58Check notation or a one the predefined aliases: 'main', 'test'."
    }
  },
  "/monitor/received_blocks/{}": {
    "GET": {
      "descr": "Monitor all newly received blocks that are not yet known by the store.",
      "args": [],
      "ret": "Object"
    }
  },
  "/monitor/validated_blocks": {
    "GET": {
      "descr": "Monitor all blocks that were successfully validated by the node but are not applied nor stored yet, disregarding whether they are going to be selected as the new head or not.",
      "args": [
        {
          "name": "protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "next_protocol",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/network": {
    "props": [
      "connections",
      "full_stat",
      "greylist",
      "log",
      "peers",
      "points",
      "self",
      "stat"
    ]
  },
  "/network/connections": {
    "GET": {
      "descr": "List the running P2P connection.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "peer_id",
      "descr": "A cryptographic node identity (Base58Check-encoded)"
    }
  },
  "/network/connections/{}": {
    "GET": {
      "descr": "Details about the current P2P connection to the given peer.",
      "args": [],
      "ret": "Object"
    },
    "DELETE": {
      "descr": "Forced close of the current P2P connection to the given peer.",
      "args": [
        {
          "name": "wait",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/network/full_stat": {
    "GET": {
      "descr": "Full network statistics.",
      "args": [],
      "ret": "Object"
    }
  },
  "/network/greylist": {
    "DELETE": {
      "descr": "Clear all greylists tables. This will unban all addresses and peers automatically greylisted by the system.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "ips",
      "peers"
    ]
  },
  "/network/greylist/ips": {
    "GET": {
      "descr": "Returns an object that contains a list of IP and the field \"not_reliable_since\".\n           If the field \"not_reliable_since\" is None then the list contains the currently greylisted IP addresses.\n           If the field \"not_reliable_since\" Contains a date, this means that the greylist has been overflowed and it is no more possible to obtain the exact list of greylisted IPs. Since the greylist of IP addresses has been design to work whatever his size, there is no security issue related to this overflow.\n          Reinitialize the ACL structure by calling \"delete /network/greylist\" to get back this list reliable.",
      "args": [],
      "ret": "Object"
    }
  },
  "/network/greylist/peers": {
    "GET": {
      "descr": "List of the last greylisted peers.",
      "args": [],
      "ret": "Array"
    }
  },
  "/network/log": {
    "GET": {
      "descr": "Stream of all network events",
      "args": [],
      "ret": "Object"
    }
  },
  "/network/peers": {
    "GET": {
      "descr": "List the peers the node ever met.",
      "args": [
        {
          "name": "filter",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "peer_id",
      "descr": "A cryptographic node identity (Base58Check-encoded)"
    }
  },
  "/network/peers/{}": {
    "GET": {
      "descr": "Details about a given peer.",
      "args": [],
      "ret": "Object"
    },
    "PATCH": {
      "descr": "Change the permissions of a given peer. With `{acl: ban}`: blacklist the given peer and remove it from the whitelist if present. With `{acl: open}`: removes the peer from the blacklist and whitelist. With `{acl: trust}`: trust the given peer permanently and remove it from the blacklist if present. The peer cannot be blocked (but its host IP still can).",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "banned",
      "log"
    ]
  },
  "/network/peers/{}/banned": {
    "GET": {
      "descr": "Check if a given peer is blacklisted or greylisted.",
      "args": [],
      "ret": "Boolean"
    }
  },
  "/network/peers/{}/log": {
    "GET": {
      "descr": "Monitor network events related to a given peer.",
      "args": [
        {
          "name": "monitor",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/network/points": {
    "GET": {
      "descr": "List the pool of known `IP:port` used for establishing P2P connections.",
      "args": [
        {
          "name": "filter",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "point",
      "descr": "A network point (ipv4:port or [ipv6]:port)."
    }
  },
  "/network/points/{}": {
    "GET": {
      "descr": "Details about a given `IP:addr`.",
      "args": [],
      "ret": "Object"
    },
    "PUT": {
      "descr": "Connect to a peer",
      "args": [
        {
          "name": "timeout",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "PATCH": {
      "descr": "Change the connectivity state of a given `IP:addr`. With `{acl : ban}`: blacklist the given address and remove it from the whitelist if present. With `{acl: open}`: removes an address from the blacklist and whitelist. With `{acl: trust}`: trust a given address permanently and remove it from the blacklist if present. With `{peer_id: <id>}` set the peerId of the point. Connections from this address can still be closed on authentication if the peer is greylisted. ",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "banned",
      "log"
    ]
  },
  "/network/points/{}/banned": {
    "GET": {
      "descr": "Check if a given address is blacklisted or greylisted. Port component is unused.",
      "args": [],
      "ret": "Boolean"
    }
  },
  "/network/points/{}/log": {
    "GET": {
      "descr": "Monitor network events related to an `IP:addr`.",
      "args": [
        {
          "name": "monitor",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/network/self": {
    "GET": {
      "descr": "Return the node's peer id",
      "args": [],
      "ret": "Object"
    }
  },
  "/network/stat": {
    "GET": {
      "descr": "Global network bandwidth statistics in B/s.",
      "args": [],
      "ret": "Object"
    }
  },
  "/private": {
    "props": [
      "injection"
    ]
  },
  "/private/injection": {
    "props": [
      "operation",
      "operations"
    ]
  },
  "/private/injection/operation": {
    "POST": {
      "descr": "Inject an operation in node and broadcast it. Returns the ID of the operation. The `signedOperationContents` should be constructed using contextual RPCs from the latest block and signed by the client. The injection of the operation will apply it on the current mempool context. This context may change at each operation injection or operation reception from peers. By default, the RPC will wait for the operation to be (pre-)validated before returning. However, if ?async is true, the function returns immediately. The optional ?chain parameter can be used to specify whether to inject on the test chain or the main chain.",
      "args": [
        {
          "name": "async",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/private/injection/operations": {
    "POST": {
      "descr": "Inject a list of operations in a node. If [force] is [true] then the operations are immediatly injected. The injection will succeed, but it does not mean the operations are (all) valid. In any case, the injection will be quick, hence [async] will be taken into account but should have almost no impact. If [async] is [true], all the promises returned by injecting an operation will be dropped. Each injection is done independently, and does not depend on the other injected operations result. Otherwise ([async]=[force]=[false]), for each operation, we record a list of promises. If all the injections succeed, the result is the list of operation hashes injected, otherwise an error (\"injection_operations_error\") is returned. This error is followed by markers for each operation: \"injection_operation_succeed\" for success and \"injection_operation_error\" for failure (followed by the errors specific to this injection).",
      "args": [
        {
          "name": "async",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "chain",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/profiler": {
    "props": [
      "registered_backend"
    ]
  },
  "/profiler/registered_backend": {
    "GET": {
      "descr": "Registered backend.",
      "args": [],
      "ret": "Object"
    }
  },
  "/protocols": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "Protocol_hash",
      "descr": "Protocol_hash (Base58Check-encoded)"
    }
  },
  "/protocols/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "environment"
    ]
  },
  "/protocols/{}/environment": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [],
      "ret": "Integer"
    }
  },
  "/stats": {
    "props": [
      "gc",
      "memory"
    ]
  },
  "/stats/gc": {
    "GET": {
      "descr": "Gets stats from the OCaml Garbage Collector",
      "args": [],
      "ret": "Object"
    }
  },
  "/stats/memory": {
    "GET": {
      "descr": "Gets memory usage stats",
      "args": [],
      "ret": "Object"
    }
  },
  "/version": {
    "GET": {
      "descr": "Get information on the node version",
      "args": [],
      "ret": "Object"
    }
  },
  "/workers": {
    "props": [
      "block_validator",
      "chain_validators",
      "prevalidators"
    ]
  },
  "/workers/block_validator": {
    "GET": {
      "descr": "Introspect the state of the block_validator worker.",
      "args": [],
      "ret": "Object"
    }
  },
  "/workers/chain_validators": {
    "GET": {
      "descr": "Lists the chain validator workers and their status.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "chain_id",
      "descr": "A chain identifier. This is either a chain hash in Base58Check notation or a one the predefined aliases: 'main', 'test'."
    }
  },
  "/workers/chain_validators/{}": {
    "GET": {
      "descr": "Introspect the state of a chain validator worker.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "ddb",
      "peers_validators"
    ]
  },
  "/workers/chain_validators/{}/ddb": {
    "GET": {
      "descr": "Introspect the state of the DDB attached to a chain validator worker.",
      "args": [],
      "ret": "Object"
    }
  },
  "/workers/chain_validators/{}/peers_validators": {
    "GET": {
      "descr": "Lists the peer validator workers and their status.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "peer_id",
      "descr": "A cryptographic node identity (Base58Check-encoded)"
    }
  },
  "/workers/chain_validators/{}/peers_validators/{}": {
    "GET": {
      "descr": "Introspect the state of a peer validator worker.",
      "args": [],
      "ret": "Object"
    }
  },
  "/workers/prevalidators": {
    "GET": {
      "descr": "Lists the Prevalidator workers and their status.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "chain_id",
      "descr": "A chain identifier. This is either a chain hash in Base58Check notation or a one the predefined aliases: 'main', 'test'."
    }
  },
  "/workers/prevalidators/{}": {
    "GET": {
      "descr": "Introspect the state of prevalidator workers.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool": {
    "props": [
      "ban_operation",
      "filter",
      "monitor_operations",
      "pending_operations",
      "request_operations",
      "unban_all_operations",
      "unban_operation"
    ]
  },
  "/chains/{}/mempool/ban_operation": {
    "POST": {
      "descr": "Remove an operation from the mempool if present. Also add it to the set of banned operations to prevent it from being fetched/processed/injected in the future. Note: If the baker has already received the operation, then it's necessary to restart it to flush the operation from it.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/filter": {
    "GET": {
      "descr": "Get the configuration of the mempool's filter and bounds. Values of the form [ \"21\", \"20\" ] are rational numbers given as a numerator and a denominator, e.g. 21/20 = 1.05. The minimal_fees (in mutez), minimal_nanotez_per_gas_unit, and minimal_nanotez_per_byte are requirements that a manager operation must meet to be considered by the mempool. replace_by_fee_factor is how much better a manager operation must be to replace a previous valid operation **from the same manager** (both its fee and its fee/gas ratio must exceed the old operation's by at least this factor). max_operations and max_total_bytes are the bounds on respectively the number of valid operations in the mempool and the sum of their sizes in bytes.",
      "args": [
        {
          "name": "include_default",
          "descr": "Show fields equal to their default value (set by default)"
        }
      ],
      "ret": "Object"
    },
    "POST": {
      "descr": "Set the configuration of the mempool's filter and bounds. **If any of the fields is absent from the input JSON, then it is set to the default value for this field (i.e. its value in the default configuration), even if it previously had a different value.** If the input JSON does not describe a valid configuration, then the configuration is left unchanged. This RPC also returns the new configuration of the mempool (which may differ from the input if the latter omits fields or is invalid). You may call [octez-client rpc get '/chains/main/mempool/filter?include_default=true'] to see an example of JSON describing a valid configuration. See the description of that RPC for details on each configurable value.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/monitor_operations": {
    "GET": {
      "descr": "Monitor the mempool operations.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "validated",
          "descr": "Include validated operations (set by default)"
        },
        {
          "name": "refused",
          "descr": "Include refused operations"
        },
        {
          "name": "outdated",
          "descr": "Include outdated operations"
        },
        {
          "name": "branch_refused",
          "descr": "Include branch refused operations"
        },
        {
          "name": "branch_delayed",
          "descr": "Include branch delayed operations (set by default)"
        },
        {
          "name": "validation_pass",
          "descr": "Include operations filtered by validation pass (all by default)"
        },
        {
          "name": "sources",
          "descr": "Include operations filtered by sources (all by default)"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/pending_operations": {
    "GET": {
      "descr": "List the prevalidated operations.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "validated",
          "descr": "Include validated operations (true by default)"
        },
        {
          "name": "refused",
          "descr": "Include refused operations (true by default)"
        },
        {
          "name": "outdated",
          "descr": "Include outdated operations (true by default)"
        },
        {
          "name": "branch_refused",
          "descr": "Include branch refused operations (true by default)"
        },
        {
          "name": "branch_delayed",
          "descr": "Include branch delayed operations (true by default)"
        },
        {
          "name": "validation_pass",
          "descr": "Include operations filtered by validation pass (all by default)"
        },
        {
          "name": "source",
          "descr": "Include operations filtered by source (all by default)"
        },
        {
          "name": "operation_hash",
          "descr": "Include operations filtered by hash (all by default)"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/request_operations": {
    "POST": {
      "descr": "Request the operations of our peers or a specific peer if specified via a query parameter.",
      "args": [
        {
          "name": "peer_id",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/unban_all_operations": {
    "POST": {
      "descr": "Clear the set of banned operations.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/mempool/unban_operation": {
    "POST": {
      "descr": "Remove an operation from the set of banned operations (nothing happens if it was not banned).",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}": {
    "GET": {
      "descr": "All the information about a block. The associated metadata may not be present depending on the history mode and block's distance from the head.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force_metadata",
          "descr": "DEPRECATED: Forces to recompute the operations metadata if it was considered as too large."
        },
        {
          "name": "metadata",
          "descr": "Specifies whether or not if the operations metadata should be returned. To get the metadata, even if it is needed to recompute them, use \"always\". To avoid getting the metadata, use \"never\". By default, the metadata will be returned depending on the node's metadata size limit policy."
        }
      ],
      "ret": "Object"
    },
    "props": [
      "context",
      "hash",
      "header",
      "helpers",
      "live_blocks",
      "metadata",
      "metadata_hash",
      "operation_hashes",
      "operation_metadata_hashes",
      "operations",
      "operations_metadata_hash",
      "protocols",
      "resulting_context_hash",
      "votes"
    ]
  },
  "/chains/{}/blocks/{}/context": {
    "props": [
      "adaptive_issuance_launch_cycle",
      "big_maps",
      "cache",
      "constants",
      "contracts",
      "dal",
      "delegates",
      "denunciations",
      "issuance",
      "liquidity_baking",
      "merkle_tree",
      "merkle_tree_v2",
      "nonces",
      "raw",
      "sapling",
      "seed",
      "seed_computation",
      "smart_rollups",
      "total_currently_staked",
      "total_frozen_stake",
      "total_supply"
    ]
  },
  "/chains/{}/blocks/{}/context/adaptive_issuance_launch_cycle": {
    "GET": {
      "descr": "Returns the cycle at which the launch of the Adaptive Issuance feature is set to happen. A result of None means that the feature is not yet set to launch.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/big_maps": {
    "item": {
      "name": "big_map_id",
      "descr": "A big map identifier"
    }
  },
  "/chains/{}/blocks/{}/context/big_maps/{}": {
    "GET": {
      "descr": "Get the (optionally paginated) list of values in a big map. Order of values is unspecified, but is guaranteed to be consistent.",
      "args": [
        {
          "name": "offset",
          "descr": "Skip the first [offset] values. Useful in combination with [length] for pagination."
        },
        {
          "name": "length",
          "descr": "Only retrieve [length] values. Useful in combination with [offset] for pagination."
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "script_expr",
      "descr": "script_expr (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/big_maps/{}/{}": {
    "GET": {
      "descr": "Access the value associated with a key in a big map.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "normalized"
    ]
  },
  "/chains/{}/blocks/{}/context/big_maps/{}/{}/normalized": {
    "POST": {
      "descr": "Access the value associated with a key in a big map, normalize the output using the requested unparsing mode.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/cache": {
    "props": [
      "contracts"
    ]
  },
  "/chains/{}/blocks/{}/context/cache/contracts": {
    "props": [
      "all",
      "rank",
      "size",
      "size_limit"
    ]
  },
  "/chains/{}/blocks/{}/context/cache/contracts/all": {
    "GET": {
      "descr": "Return the list of cached contracts",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/cache/contracts/rank": {
    "POST": {
      "descr": "Return the number of cached contracts older than the provided contract",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/cache/contracts/size": {
    "GET": {
      "descr": "Return the size of the contract cache",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/cache/contracts/size_limit": {
    "GET": {
      "descr": "Return the size limit of the contract cache",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/constants": {
    "GET": {
      "descr": "All constants",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "errors",
      "parametric"
    ]
  },
  "/chains/{}/blocks/{}/context/constants/errors": {
    "GET": {
      "descr": "Schema for all the RPC errors from this protocol version",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/constants/parametric": {
    "GET": {
      "descr": "Parametric constants",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts": {
    "GET": {
      "descr": "All existing contracts (excluding empty implicit contracts).",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "contract_id",
      "descr": "A contract identifier encoded in b58check."
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}": {
    "GET": {
      "descr": "Access the complete status of a contract.",
      "args": [
        {
          "name": "normalize_types",
          "descr": "Whether types should be normalized (annotations removed, combs flattened) or kept as they appeared in the original script."
        }
      ],
      "ret": "Object"
    },
    "props": [
      "all_ticket_balances",
      "balance",
      "balance_and_frozen_bonds",
      "big_map_get",
      "counter",
      "delegate",
      "entrypoints",
      "estimated_own_pending_slashed_amount",
      "frozen_bonds",
      "full_balance",
      "manager_key",
      "script",
      "single_sapling_get_diff",
      "spendable",
      "spendable_and_frozen_bonds",
      "staked_balance",
      "staking_numerator",
      "storage",
      "ticket_balance",
      "unstake_requests",
      "unstaked_finalizable_balance",
      "unstaked_frozen_balance"
    ]
  },
  "/chains/{}/blocks/{}/context/contracts/{}/all_ticket_balances": {
    "GET": {
      "descr": "Access the complete list of tickets owned by the given contract by scanning the contract's storage.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/balance": {
    "GET": {
      "descr": "The spendable balance of a contract (in mutez), also known as liquid balance. Corresponds to tez owned by the contract that are neither staked, nor in unstaked requests, nor in frozen bonds. Identical to the 'spendable' RPC.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/balance_and_frozen_bonds": {
    "GET": {
      "descr": "The sum (in mutez) of the spendable balance and frozen bonds of a contract. Corresponds to the contract's full balance from which staked funds and unstake requests have been excluded. Identical to the 'spendable_and_frozen_bonds' RPC.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/big_map_get": {
    "POST": {
      "descr": "Access the value associated with a key in a big map of the contract (deprecated).",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/counter": {
    "GET": {
      "descr": "Access the counter of a contract, if any.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/delegate": {
    "GET": {
      "descr": "Access the delegate of a contract, if any.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/entrypoints": {
    "GET": {
      "descr": "Return the list of entrypoints of the contract",
      "args": [
        {
          "name": "normalize_types",
          "descr": "Whether types should be normalized (annotations removed, combs flattened) or kept as they appeared in the original script."
        }
      ],
      "ret": "Object"
    },
    "item": {
      "name": "entrypoint",
      "descr": "A Michelson entrypoint (string of length < 32)"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/entrypoints/{}": {
    "GET": {
      "descr": "Return the type of the given entrypoint of the contract",
      "args": [
        {
          "name": "normalize_types",
          "descr": "Whether types should be normalized (annotations removed, combs flattened) or kept as they appeared in the original script."
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/estimated_own_pending_slashed_amount": {
    "GET": {
      "descr": "Returns the estimated own pending slashed amount (in mutez) of a given contract.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/frozen_bonds": {
    "GET": {
      "descr": "Access the frozen bonds of a contract.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/full_balance": {
    "GET": {
      "descr": "The full balance (in mutez) of the contract. Includes its spendable balance, staked tez, unstake requests, and frozen bonds. Even if the contract is a delegate, it does not include any staked or delegated tez owned by external delegators.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/manager_key": {
    "GET": {
      "descr": "Access the manager of an implicit contract.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/script": {
    "GET": {
      "descr": "Access the code and data of the contract.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "normalized"
    ]
  },
  "/chains/{}/blocks/{}/context/contracts/{}/script/normalized": {
    "POST": {
      "descr": "Access the script of the contract and normalize it using the requested unparsing mode.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/single_sapling_get_diff": {
    "GET": {
      "descr": "Returns the root and a diff of a state starting from an optional offset which is zero by default.",
      "args": [
        {
          "name": "offset_commitment",
          "descr": "Commitments and ciphertexts are returned from the specified offset up to the most recent."
        },
        {
          "name": "offset_nullifier",
          "descr": "Nullifiers are returned from the specified offset up to the most recent."
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/spendable": {
    "GET": {
      "descr": "The spendable balance of a contract (in mutez), also known as liquid balance. Corresponds to tez owned by the contract that are neither staked, nor in unstaked requests, nor in frozen bonds. Identical to the 'balance' RPC.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/spendable_and_frozen_bonds": {
    "GET": {
      "descr": "The sum (in mutez) of the spendable balance and frozen bonds of a contract. Corresponds to the contract's full balance from which staked funds and unstake requests have been excluded. Identical to the 'balance_and_frozen_bonds' RPC.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/staked_balance": {
    "GET": {
      "descr": "Access the staked balance of a contract (in mutez). Returns None if the contract is originated, or neither delegated nor a delegate.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/staking_numerator": {
    "GET": {
      "descr": "Returns an abstract representation of the contract's total_delegated_stake.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/storage": {
    "GET": {
      "descr": "Access the data of the contract.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "normalized",
      "paid_space",
      "used_space"
    ]
  },
  "/chains/{}/blocks/{}/context/contracts/{}/storage/normalized": {
    "POST": {
      "descr": "Access the data of the contract and normalize it using the requested unparsing mode.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/storage/paid_space": {
    "GET": {
      "descr": "Access the paid storage space of the contract.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/storage/used_space": {
    "GET": {
      "descr": "Access the used storage space of the contract.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/ticket_balance": {
    "POST": {
      "descr": "Access the contract's balance of ticket with specified ticketer, content type, and content.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/unstake_requests": {
    "GET": {
      "descr": "Access the unstake requests of the contract. The requests that appear in the finalizable field can be finalized, which means that the contract can transfer these (no longer frozen) funds to their spendable balance with a [finalize_unstake] operation call. Returns None if there is no unstake request pending.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/unstaked_finalizable_balance": {
    "GET": {
      "descr": "Access the balance of a contract that was requested for an unstake operation, and is no longer frozen, which means it will appear in the spendable balance of the contract after any stake/unstake/finalize_unstake operation. Returns None if the contract is originated.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/contracts/{}/unstaked_frozen_balance": {
    "GET": {
      "descr": "Access the balance of a contract that was requested for an unstake operation, but is still frozen for the duration of the slashing period. Returns None if the contract is originated.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/dal": {
    "props": [
      "commitments_history",
      "published_slot_headers",
      "shards"
    ]
  },
  "/chains/{}/blocks/{}/context/dal/commitments_history": {
    "GET": {
      "descr": "Returns the (currently last) DAL skip list cell if DAL is enabled, or [None] otherwise.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/dal/published_slot_headers": {
    "GET": {
      "descr": "Get the published slots headers for the given level",
      "args": [
        {
          "name": "level",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/dal/shards": {
    "GET": {
      "descr": "Get the shards assignment for a given level (the default is the current level) and given delegates (the default is all delegates)",
      "args": [
        {
          "name": "level",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "delegates",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates": {
    "GET": {
      "descr": "Lists all registered delegates by default. The arguments `active`, `inactive`, `with_minimal_stake`, and `without_minimal_stake` allow to enumerate only the delegates that are active, inactive, have at least a minimal stake to participate in consensus and in governance, or do not have such a minimal stake, respectively. Note, setting these arguments to false has no effect.",
      "args": [
        {
          "name": "active",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "inactive",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "with_minimal_stake",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "without_minimal_stake",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}": {
    "GET": {
      "descr": "Everything about a delegate. Gathers the outputs of all RPCs with the ../delegates/<pkh> prefix.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "active_staking_parameters",
      "baking_power",
      "consensus_key",
      "current_baking_power",
      "current_frozen_deposits",
      "current_voting_power",
      "deactivated",
      "delegated_balance",
      "delegated_contracts",
      "delegators",
      "denunciations",
      "estimated_shared_pending_slashed_amount",
      "external_delegated",
      "external_staked",
      "frozen_deposits",
      "frozen_deposits_limit",
      "full_balance",
      "grace_period",
      "is_forbidden",
      "min_delegated_in_current_cycle",
      "own_delegated",
      "own_full_balance",
      "own_staked",
      "participation",
      "pending_staking_parameters",
      "stakers",
      "staking_balance",
      "staking_denominator",
      "total_delegated",
      "total_delegated_stake",
      "total_staked",
      "total_unstaked_per_cycle",
      "unstaked_frozen_deposits",
      "voting_info",
      "voting_power"
    ]
  },
  "/chains/{}/blocks/{}/context/delegates/{}/active_staking_parameters": {
    "GET": {
      "descr": "Returns the currently active staking parameters for the given delegate.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/baking_power": {
    "GET": {
      "descr": "The current baking power of a delegate, using the current staked and delegated balances of the baker and its delegators. In other words, the baking rights that the baker would get for a future cycle if the current cycle ended right at the current block.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/consensus_key": {
    "GET": {
      "descr": "The active consensus key for a given delegate and the pending consensus keys.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/current_baking_power": {
    "GET": {
      "descr": "DEPRECATED; use baking_power instead.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/current_frozen_deposits": {
    "GET": {
      "descr": "DEPRECATED; use total_staked instead.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/current_voting_power": {
    "GET": {
      "descr": "The voting power of a given delegate, as computed from its current stake.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/deactivated": {
    "GET": {
      "descr": "Tells whether the delegate is currently tagged as deactivated or not.",
      "args": [],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/delegated_balance": {
    "GET": {
      "descr": "DEPRECATED; to get this value, you can call RPCs external_staked and external_delegated, and add their outputs together.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/delegated_contracts": {
    "GET": {
      "descr": "DEPRECATED; use delegators instead.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/delegators": {
    "GET": {
      "descr": "The list of all contracts that are currently delegating to the delegate. Includes both user accounts and smart contracts. Includes the delegate itself.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/denunciations": {
    "GET": {
      "descr": "Returns the pending denunciations for the given delegate.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/estimated_shared_pending_slashed_amount": {
    "GET": {
      "descr": "Returns the estimated shared pending slashed amount (in mutez) of a given delegate.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/external_delegated": {
    "GET": {
      "descr": "The sum (in mutez) of non-staked tokens that currently count as delegated to the baker, excluding those owned by the baker iself. Does not take limits such as overstaking or overdelegation into account. This includes the spendable balances and frozen bonds of all the baker's external delegators. It also includes unstake requests of contracts other than the baker, on the condition that the contract was delegating to the baker at the time of the unstake operation. So this includes most but not all unstake requests from current delegators, and might include some unstake requests from old delegators. Limits such as overstaking and overdelegation have not been applied yet.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/external_staked": {
    "GET": {
      "descr": "The sum (in mutez) of all tokens currently staked by the baker's external delegators. This excludes the baker's own staked tokens.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/frozen_deposits": {
    "GET": {
      "descr": "DEPRECATED; call RPC total_staked on the last block of (current_cycle - 3) instead. Returns the total amount (in mutez) that was staked for the baker by all stakers (including the baker itself) at the time the staking rights for the current cycle were computed.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/frozen_deposits_limit": {
    "GET": {
      "descr": "DEPRECATED; the frozen deposits limit has no effects since the activation of Adaptive Issuance and Staking during the Paris protocol.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/full_balance": {
    "GET": {
      "descr": "DEPRECATED; use own_full_balance instead.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/grace_period": {
    "GET": {
      "descr": "Returns the cycle by the end of which the delegate might be deactivated if she fails to execute any delegate action. A deactivated delegate might be reactivated (without loosing any stake) by simply re-registering as a delegate. For deactivated delegates, this value contains the cycle at which they were deactivated.",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/is_forbidden": {
    "GET": {
      "descr": "Returns true if the delegate is forbidden to participate in consensus.",
      "args": [],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/min_delegated_in_current_cycle": {
    "GET": {
      "descr": "Returns the minimum of delegated tez (in mutez) during the current cycle and the block level at the end of which the minimum was reached. This only takes into account the value of `total_delegated` at the end of each block, not in the middle of applying operations. This is the delegated amount that would be used to compute the delegate's future baking rights if the cycle ended at the current block. If the minimum was reached multiple times, the returned level is the earliest level of the current cycle that reached this minimum. For instance, if `total_delegated` hasn't changed at all since the beginning of the current cycle, returns the first level of the current cycle. (If the contract is not registered as a delegate, returns 0 mutez and omits the level.)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/own_delegated": {
    "GET": {
      "descr": "The amount (in mutez) currently owned by the baker itself and counting as delegated for the purpose of baking rights. This corresponds to all non-staked tokens owned by the baker: spendable balance, frozen bonds, and unstake requests. (Note: There is one exception: if the baker still has unstake requests created at a time when it was delegating to a different delegate, then these unstake requests still count as delegated to the former delegate. Any such unstake requests are excluded from the amount returned by the present RPC, despite being non-staked tokens owned by the baker.)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/own_full_balance": {
    "GET": {
      "descr": "The full balance (in mutez) of tokens owned by the delegate itself. Includes its spendable balance, staked tez, unstake requests, and frozen bonds. Does not include any tokens owned by external delegators. This RPC fails when the pkh is not a delegate. When it is a delegate, this RPC outputs the same amount as ../<block_id>/context/contracts/<delegate_contract_id>/full_balance.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/own_staked": {
    "GET": {
      "descr": "The amount (in mutez) currently owned and staked by the baker itself. Returns the same value as ../<block_id>/context/contracts/<delegate_contract_id>/staked_balance (except for the fact that the present RPC fails if the public_key_hash in the path is not a delegate).",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/participation": {
    "GET": {
      "descr": "Returns cycle and level participation information. In particular this indicates, in the field 'expected_cycle_activity', the number of slots the delegate is expected to have in the cycle based on its active stake. The field 'minimal_cycle_activity' indicates the minimal attesting slots in the cycle required to get attesting rewards. It is computed based on 'expected_cycle_activity. The fields 'missed_slots' and 'missed_levels' indicate the number of missed attesting slots and missed levels (for attesting) in the cycle so far. 'missed_slots' indicates the number of missed attesting slots in the cycle so far. The field 'remaining_allowed_missed_slots' indicates the remaining amount of attesting slots that can be missed in the cycle before forfeiting the rewards. Finally, 'expected_attesting_rewards' indicates the attesting rewards that will be distributed at the end of the cycle if activity at that point will be greater than the minimal required; if the activity is already known to be below the required minimum, then the rewards are zero.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/pending_staking_parameters": {
    "GET": {
      "descr": "Returns the pending values for the given delegate's staking parameters.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/stakers": {
    "GET": {
      "descr": "Returns the list of accounts that stake to a given delegate together with their share of the frozen deposits.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/staking_balance": {
    "GET": {
      "descr": "DEPRECATED; to get this value, you can call RPCs total_staked and total_delegated, and add their outputs together.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/staking_denominator": {
    "GET": {
      "descr": "Returns an abstract representation of the total delegated stake.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/total_delegated": {
    "GET": {
      "descr": "All tokens (in mutez) that currently count as delegated for the purpose of computing the baker's rights; they weigh half as much as staked tez in the rights. Limits such as overstaking and overdelegation have not been applied yet. This corresponds to all non-staked tez owned by the baker's delegators (including the baker itself): spendable balances, frozen bonds, and unstaked requests, except for any unstake requests that have been created before the delegator changed its delegate to the current baker (because they still count as delegated for the old delegate instead).",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/total_delegated_stake": {
    "GET": {
      "descr": "DEPRECATED; use external_staked instead.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/total_staked": {
    "GET": {
      "descr": "The total amount (in mutez) currently staked for the baker, both by the baker itself and by external stakers. This is the staked amount before applying the baker's 'limit_of_staking_over_baking'; in other words, it includes overstaked tez if there are any.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/total_unstaked_per_cycle": {
    "GET": {
      "descr": "For each cycle, returns the total amount (in mutez) contained in all unstake requests created during this cycle by all delegators, including the baker itself. Note that these tokens count as delegated to the baker for the purpose of computing baking rights, and are included in the amount returned by the total_delegated RPC.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/unstaked_frozen_deposits": {
    "GET": {
      "descr": "DEPRECATED; use total_unstaked_per_cycle instead.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/voting_info": {
    "GET": {
      "descr": "Returns the delegate info (e.g. voting power) found in the listings of the current voting period.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/delegates/{}/voting_power": {
    "GET": {
      "descr": "The voting power in the vote listings for a given delegate.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/denunciations": {
    "GET": {
      "descr": "Returns the denunciations for misbehavior in the current cycle.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/issuance": {
    "props": [
      "current_yearly_rate",
      "current_yearly_rate_details",
      "current_yearly_rate_exact",
      "expected_issuance",
      "issuance_per_minute"
    ]
  },
  "/chains/{}/blocks/{}/context/issuance/current_yearly_rate": {
    "GET": {
      "descr": "Returns the current expected maximum yearly issuance rate (in %). The value only includes participation rewards (and does not include liquidity baking)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/issuance/current_yearly_rate_details": {
    "GET": {
      "descr": "Returns the static and dynamic parts of the current expected maximum yearly issuance rate (in %). The value only includes participation rewards (and does not include liquidity baking)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/issuance/current_yearly_rate_exact": {
    "GET": {
      "descr": "Returns the current expected maximum yearly issuance rate (exact quotient) (in %). The value only includes participation rewards (and does not include liquidity baking)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/issuance/expected_issuance": {
    "GET": {
      "descr": "Returns the expected issued tez for the provided block and the next 'consensus_rights_delay' cycles (in mutez)",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/issuance/issuance_per_minute": {
    "GET": {
      "descr": "Returns the current expected maximum issuance per minute (in mutez). The value only includes participation rewards (and does not include liquidity baking)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/liquidity_baking": {
    "props": [
      "cpmm_address"
    ]
  },
  "/chains/{}/blocks/{}/context/liquidity_baking/cpmm_address": {
    "GET": {
      "descr": "Liquidity baking CPMM address",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/merkle_tree": {
    "GET": {
      "descr": "Returns the merkle tree of a piece of context.",
      "args": [
        {
          "name": "holey",
          "descr": "Send only hashes, omit data of key"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/merkle_tree_v2": {
    "GET": {
      "descr": "Returns the Irmin merkle tree of a piece of context.",
      "args": [
        {
          "name": "holey",
          "descr": "Send only hashes, omit data of key"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/nonces": {
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/nonces/{}": {
    "GET": {
      "descr": "Info about the nonce of a previous block.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw": {
    "props": [
      "bytes",
      "json"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/bytes": {
    "GET": {
      "descr": "Returns the raw context.",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/sapling": {
    "item": {
      "name": "sapling_state_id",
      "descr": "A sapling state identifier"
    }
  },
  "/chains/{}/blocks/{}/context/sapling/{}": {
    "props": [
      "get_diff"
    ]
  },
  "/chains/{}/blocks/{}/context/sapling/{}/get_diff": {
    "GET": {
      "descr": "Returns the root and a diff of a state starting from an optional offset which is zero by default.",
      "args": [
        {
          "name": "offset_commitment",
          "descr": "Commitments and ciphertexts are returned from the specified offset up to the most recent."
        },
        {
          "name": "offset_nullifier",
          "descr": "Nullifiers are returned from the specified offset up to the most recent."
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/seed": {
    "POST": {
      "descr": "Seed of the cycle to which the block belongs.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/seed_computation": {
    "GET": {
      "descr": "Seed computation status",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups": {
    "props": [
      "all",
      "smart_rollup"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/all": {
    "GET": {
      "descr": "List of all originated smart rollups",
      "args": [],
      "ret": "Array"
    },
    "props": [
      "inbox"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/all/inbox": {
    "GET": {
      "descr": "Inbox for the smart rollups",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup": {
    "item": {
      "name": "smart_rollup_address",
      "descr": "smart_rollup_address (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}": {
    "props": [
      "commitment",
      "consumed_outputs",
      "genesis_info",
      "inbox_level",
      "kind",
      "last_cemented_commitment_hash_with_level",
      "last_whitelist_update",
      "staker",
      "staker1",
      "stakers",
      "ticket_balance",
      "whitelist"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/commitment": {
    "item": {
      "name": "smart_rollup_commitment_hash",
      "descr": "smart_rollup_commitment_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/commitment/{}": {
    "GET": {
      "descr": "Commitment for a smart rollup from its hash",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "can_be_cemented",
      "stakers_indexes"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/commitment/{}/can_be_cemented": {
    "GET": {
      "descr": "Returns true if and only if the provided commitment can be cemented.",
      "args": [],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/commitment/{}/stakers_indexes": {
    "GET": {
      "descr": "List of stakers indexes staking on a given commitment",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/consumed_outputs": {
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/consumed_outputs/{}": {
    "GET": {
      "descr": "Return the known consumed outputs of a smart rollup.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/genesis_info": {
    "GET": {
      "descr": "Genesis information (level and commitment hash) for a smart rollup",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/inbox_level": {
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/inbox_level/{}": {
    "props": [
      "commitments"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/inbox_level/{}/commitments": {
    "GET": {
      "descr": "List of commitments associated to a rollup for a given inbox level",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/kind": {
    "GET": {
      "descr": "Kind of smart rollup",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/last_cemented_commitment_hash_with_level": {
    "GET": {
      "descr": "Level and hash of the last cemented commitment for a smart rollup",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/last_whitelist_update": {
    "GET": {
      "descr": "Last whitelist update for private smart rollups. If the output is None then the rollup is public.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker": {
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker/{}": {
    "props": [
      "conflicts",
      "games",
      "index",
      "staked_on_commitment"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker/{}/conflicts": {
    "GET": {
      "descr": "List of stakers in conflict with the given staker",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker/{}/games": {
    "GET": {
      "descr": "Ongoing refutation games for a given staker",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker/{}/index": {
    "GET": {
      "descr": "Staker index associated to a public key hash for a given rollup",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker/{}/staked_on_commitment": {
    "GET": {
      "descr": "The newest commitment on which the operator has staked on for a smart rollup. Note that is can return a commitment that is before the last cemented one.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1": {
    "item": {
      "name": "staker1_pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1/{}": {
    "props": [
      "staker2"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1/{}/staker2": {
    "item": {
      "name": "staker2_pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1/{}/staker2/{}": {
    "props": [
      "timeout",
      "timeout_reached"
    ]
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1/{}/staker2/{}/timeout": {
    "GET": {
      "descr": "Returns the timeout of players.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/staker1/{}/staker2/{}/timeout_reached": {
    "GET": {
      "descr": "Returns whether the timeout creates a result for the game.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/stakers": {
    "GET": {
      "descr": "List of active stakers' public key hashes of a rollup",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/ticket_balance": {
    "POST": {
      "descr": "Access the smart rollup's balance of ticket with specified ticketer, content type, and content.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/smart_rollups/smart_rollup/{}/whitelist": {
    "GET": {
      "descr": "Whitelist for private smart rollups. If the output is None then the rollup is public.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/total_currently_staked": {
    "GET": {
      "descr": "Returns the amount of staked tez by delegates, delegators or overstaked.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/total_frozen_stake": {
    "GET": {
      "descr": "Returns the total stake (in mutez) frozen on the chain",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/total_supply": {
    "GET": {
      "descr": "Returns the total supply (in mutez) available on the chain",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/hash": {
    "GET": {
      "descr": "The block's hash, its unique identifier.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/header": {
    "GET": {
      "descr": "The whole block header.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "protocol_data",
      "raw",
      "shell"
    ]
  },
  "/chains/{}/blocks/{}/header/protocol_data": {
    "GET": {
      "descr": "The version-specific fragment of the block header.",
      "args": [],
      "ret": "Object"
    },
    "props": [
      "raw"
    ]
  },
  "/chains/{}/blocks/{}/header/protocol_data/raw": {
    "GET": {
      "descr": "The version-specific fragment of the block header (unparsed).",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/header/raw": {
    "GET": {
      "descr": "The whole block header (unparsed).",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/header/shell": {
    "GET": {
      "descr": "The shell-specific fragment of the block header.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers": {
    "props": [
      "attestation_rights",
      "baking_rights",
      "complete",
      "current_level",
      "forge",
      "forge_block_header",
      "levels_in_current_cycle",
      "parse",
      "preapply",
      "round",
      "scripts",
      "validators"
    ]
  },
  "/chains/{}/blocks/{}/helpers/attestation_rights": {
    "GET": {
      "descr": "Retrieves the delegates allowed to attest a block.\nBy default, it gives the attestation power for delegates that have at least one attestation slot for the next block.\nParameters `level` and `cycle` can be used to specify the (valid) level(s) in the past or future at which the attestation rights have to be returned. Parameter `delegate` can be used to restrict the results to the given delegates.\nParameter `consensus_key` can be used to restrict the results to the given consensus_keys. \nReturns the smallest attestation slots and the attestation power. Also returns the minimal timestamp that corresponds to attestation at the given level. The timestamps are omitted for levels in the past, and are only estimates for levels higher that the next block's, based on the hypothesis that all predecessor blocks were baked at the first round.",
      "args": [
        {
          "name": "level",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "cycle",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "delegate",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "consensus_key",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/helpers/baking_rights": {
    "GET": {
      "descr": "Retrieves the list of delegates allowed to bake a block.\nBy default, it gives the best baking opportunities (in terms of rounds) for bakers that have at least one opportunity below the 64th round for the next block.\nParameters `level` and `cycle` can be used to specify the (valid) level(s) in the past or future at which the baking rights have to be returned.\nParameter `delegate` can be used to restrict the results to the given delegates. Parameter `consensus_key` can be used to restrict the results to the given consensus_keys. If parameter `all` is set, all the baking opportunities for each baker at each level are returned, instead of just the first one.\nReturns the list of baking opportunities up to round 64. Also returns the minimal timestamps that correspond to these opportunities. The timestamps are omitted for levels in the past, and are only estimates for levels higher that the next block's, based on the hypothesis that all predecessor blocks were baked at the first round.",
      "args": [
        {
          "name": "level",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "cycle",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "delegate",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "consensus_key",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "max_round",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "all",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/helpers/complete": {
    "item": {
      "name": "prefix",
      "descr": "\u00af\\_(\u30c4)_/\u00af"
    }
  },
  "/chains/{}/blocks/{}/helpers/complete/{}": {
    "GET": {
      "descr": "Try to complete a prefix of a Base58Check-encoded data. This RPC is actually able to complete hashes of block, operations, public_keys and contracts.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/helpers/current_level": {
    "GET": {
      "descr": "Returns the level of the interrogated block, or the one of a block located `offset` blocks after it in the chain. For instance, the next block if `offset` is 1. The offset cannot be negative.",
      "args": [
        {
          "name": "offset",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/forge": {
    "props": [
      "operations",
      "protocol_data"
    ]
  },
  "/chains/{}/blocks/{}/helpers/forge/operations": {
    "POST": {
      "descr": "Forge an operation",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/helpers/forge/protocol_data": {
    "POST": {
      "descr": "Forge the protocol-specific part of a block header",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/forge_block_header": {
    "POST": {
      "descr": "Forge a block header",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/levels_in_current_cycle": {
    "GET": {
      "descr": "Levels of a cycle",
      "args": [
        {
          "name": "offset",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/parse": {
    "props": [
      "block",
      "operations"
    ]
  },
  "/chains/{}/blocks/{}/helpers/parse/block": {
    "POST": {
      "descr": "Parse a block",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/parse/operations": {
    "POST": {
      "descr": "Parse operations",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/helpers/preapply": {
    "props": [
      "block",
      "operations"
    ]
  },
  "/chains/{}/blocks/{}/helpers/preapply/block": {
    "POST": {
      "descr": "Simulate the validation of a block that would contain the given operations and return the resulting fitness and context hash.",
      "args": [
        {
          "name": "sort",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "timestamp",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/preapply/operations": {
    "POST": {
      "descr": "Simulate the application of the operations with the context of the given block and return the result of each operation application.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/round": {
    "GET": {
      "descr": "Returns the round of the interrogated block, or the one of a block located `offset` blocks after in the chain (or before when negative). For instance, the next block if `offset` is 1.",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts": {
    "props": [
      "entrypoint",
      "entrypoints",
      "normalize_data",
      "normalize_script",
      "normalize_stack",
      "normalize_type",
      "pack_data",
      "run_code",
      "run_instruction",
      "run_operation",
      "run_script_view",
      "run_view",
      "script_size",
      "simulate_operation",
      "trace_code",
      "typecheck_code",
      "typecheck_data"
    ]
  },
  "/chains/{}/blocks/{}/helpers/scripts/entrypoint": {
    "POST": {
      "descr": "Return the type of the given entrypoint",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/entrypoints": {
    "POST": {
      "descr": "Return the list of entrypoints of the given script",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/normalize_data": {
    "POST": {
      "descr": "Normalizes some data expression using the requested unparsing mode",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/normalize_script": {
    "POST": {
      "descr": "Normalizes a Michelson script using the requested unparsing mode",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/normalize_stack": {
    "POST": {
      "descr": "Normalize a Michelson stack using the requested unparsing mode",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/normalize_type": {
    "POST": {
      "descr": "Normalizes some Michelson type by expanding `pair a b c` as `pair a (pair b c)",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/pack_data": {
    "POST": {
      "descr": "Computes the serialized version of some data expression using the same algorithm as script instruction PACK",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/run_code": {
    "POST": {
      "descr": "Run a Michelson script in the current context",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/run_instruction": {
    "POST": {
      "descr": "Run a single Michelson instruction",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/run_operation": {
    "POST": {
      "descr": "Run an operation with the context of the given block and without signature checks. Return the operation application result, including the consumed gas. This RPC does not support consensus operations.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/run_script_view": {
    "POST": {
      "descr": "Simulate a call to a michelson view",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/run_view": {
    "POST": {
      "descr": "Simulate a call to a view following the TZIP-4 standard. See https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-4/tzip-4.md#view-entrypoints.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/script_size": {
    "POST": {
      "descr": "Compute the size of a script in the current context",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/simulate_operation": {
    "POST": {
      "descr": "Simulate running an operation at some future moment (based on the number of blocks given in the `latency` argument), and return the operation application result. The result is the same as run_operation except for the consumed gas, which depends on the contents of the cache at that future moment. This RPC estimates future gas consumption by trying to predict the state of the cache using some heuristics.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "successor_level",
          "descr": "If true, the simulation is done on the successor level of the current context."
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/trace_code": {
    "POST": {
      "descr": "Run a Michelson script in the current context, keeping a trace",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/typecheck_code": {
    "POST": {
      "descr": "Typecheck a piece of code in the current context",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/scripts/typecheck_data": {
    "POST": {
      "descr": "Check that some data expression is well formed and of a given type in the current context",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/helpers/validators": {
    "GET": {
      "descr": "Retrieves the level, the attestation slots and the public key hash of each delegate allowed to attest a block.\nBy default, it provides this information for the next level.\nParameter `level` can be used to specify the (valid) level(s) in the past or future at which the attestation rights have to be returned. Parameter `delegate` can be used to restrict the results results to the given delegates. Parameter `consensus_key` can be used to restrict the results to the given consensus_keys.\n",
      "args": [
        {
          "name": "level",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "delegate",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "consensus_key",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/live_blocks": {
    "GET": {
      "descr": "List the ancestors of the given block which, if referred to as the branch in an operation header, are recent enough for that operation to be included in the current block.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/metadata": {
    "GET": {
      "descr": "All the metadata associated to the block.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/metadata_hash": {
    "GET": {
      "descr": "Hash of the metadata associated to the block. This is only set on blocks starting from environment V1.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/operation_hashes": {
    "GET": {
      "descr": "The hashes of all the operations included in the block.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "list_offset",
      "descr": "Index `n` of the requested validation pass."
    }
  },
  "/chains/{}/blocks/{}/operation_hashes/{}": {
    "GET": {
      "descr": "All the operations included in `n-th` validation pass of the block.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "operation_offset",
      "descr": "Index `m` of the requested operation in its validation pass."
    }
  },
  "/chains/{}/blocks/{}/operation_hashes/{}/{}": {
    "GET": {
      "descr": "The hash of then `m-th` operation in the `n-th` validation pass of the block.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/operation_metadata_hashes": {
    "GET": {
      "descr": "The hashes of all the operation metadata included in the block. This is only set on blocks starting from environment V1.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "list_offset",
      "descr": "Index `n` of the requested validation pass."
    }
  },
  "/chains/{}/blocks/{}/operation_metadata_hashes/{}": {
    "GET": {
      "descr": "All the operation metadata included in `n-th` validation pass of the block. This is only set on blocks starting from environment V1.",
      "args": [],
      "ret": "Array"
    },
    "item": {
      "name": "operation_offset",
      "descr": "Index `m` of the requested operation in its validation pass."
    }
  },
  "/chains/{}/blocks/{}/operation_metadata_hashes/{}/{}": {
    "GET": {
      "descr": "The hash of then `m-th` operation metadata in the `n-th` validation pass of the block. This is only set on blocks starting from environment V1.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/operations": {
    "GET": {
      "descr": "All the operations included in the block.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force_metadata",
          "descr": "DEPRECATED: Forces to recompute the operations metadata if it was considered as too large."
        },
        {
          "name": "metadata",
          "descr": "Specifies whether or not if the operations metadata should be returned. To get the metadata, even if it is needed to recompute them, use \"always\". To avoid getting the metadata, use \"never\". By default, the metadata will be returned depending on the node's metadata size limit policy."
        }
      ],
      "ret": "Object"
    },
    "item": {
      "name": "list_offset",
      "descr": "Index `n` of the requested validation pass."
    }
  },
  "/chains/{}/blocks/{}/operations/{}": {
    "GET": {
      "descr": "All the operations included in `n-th` validation pass of the block.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force_metadata",
          "descr": "DEPRECATED: Forces to recompute the operations metadata if it was considered as too large."
        },
        {
          "name": "metadata",
          "descr": "Specifies whether or not if the operations metadata should be returned. To get the metadata, even if it is needed to recompute them, use \"always\". To avoid getting the metadata, use \"never\". By default, the metadata will be returned depending on the node's metadata size limit policy."
        }
      ],
      "ret": "Object"
    },
    "item": {
      "name": "operation_offset",
      "descr": "Index `m` of the requested operation in its validation pass."
    }
  },
  "/chains/{}/blocks/{}/operations/{}/{}": {
    "GET": {
      "descr": "The `m-th` operation in the `n-th` validation pass of the block.",
      "args": [
        {
          "name": "version",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        },
        {
          "name": "force_metadata",
          "descr": "DEPRECATED: Forces to recompute the operations metadata if it was considered as too large."
        },
        {
          "name": "metadata",
          "descr": "Specifies whether or not if the operations metadata should be returned. To get the metadata, even if it is needed to recompute them, use \"always\". To avoid getting the metadata, use \"never\". By default, the metadata will be returned depending on the node's metadata size limit policy."
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/operations_metadata_hash": {
    "GET": {
      "descr": "The root hash of the operations metadata from the block. This is only set on blocks starting from environment V1.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/protocols": {
    "GET": {
      "descr": "Current and next protocol.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/resulting_context_hash": {
    "GET": {
      "descr": "Context hash resulting of the block application.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/votes": {
    "props": [
      "ballot_list",
      "ballots",
      "current_period",
      "current_proposal",
      "current_quorum",
      "listings",
      "proposal_count",
      "proposals",
      "successor_period",
      "total_voting_power"
    ]
  },
  "/chains/{}/blocks/{}/votes/ballot_list": {
    "GET": {
      "descr": "Ballots casted so far during a voting period.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/votes/ballots": {
    "GET": {
      "descr": "Sum of ballots casted so far during a voting period.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/votes/current_period": {
    "GET": {
      "descr": "Returns the voting period (index, kind, starting position) and related information (position, remaining) of the interrogated block.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/votes/current_proposal": {
    "GET": {
      "descr": "Current proposal under evaluation.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/votes/current_quorum": {
    "GET": {
      "descr": "Current expected quorum.",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/votes/listings": {
    "GET": {
      "descr": "List of delegates with their voting power.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/votes/proposal_count": {
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/votes/proposal_count/{}": {
    "GET": {
      "descr": "Number of votes casted during the current period.",
      "args": [],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/votes/proposals": {
    "GET": {
      "descr": "List of proposals with number of supporters.",
      "args": [],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/votes/successor_period": {
    "GET": {
      "descr": "Returns the voting period (index, kind, starting position) and related information (position, remaining) of the next block.Useful to craft operations that will be valid in the next block.",
      "args": [],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/votes/total_voting_power": {
    "GET": {
      "descr": "Total voting power in the voting listings.",
      "args": [],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "active_delegates_with_minimal_stake",
      "adaptive_issuance_ema",
      "adaptive_issuance_launch_cycle",
      "attestation_branch",
      "big_maps",
      "block_round",
      "commitments",
      "consensus_keys",
      "contracts",
      "cycle",
      "dal",
      "delegates",
      "denunciations",
      "first_level_of_protocol",
      "forbidden_delegates",
      "global_constant",
      "grand_parent_branch",
      "liquidity_baking_cpmm_address",
      "liquidity_baking_escape_ema",
      "pending_migration_balance_updates",
      "pending_migration_operation_results",
      "ramp_up",
      "sapling",
      "seed_status",
      "slashed_deposits",
      "smart_rollup",
      "staking_balance",
      "ticket_balance",
      "vdf_challenge",
      "votes",
      "zk_rollup"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/active_delegates_with_minimal_stake": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/active_delegates_with_minimal_stake/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/adaptive_issuance_ema": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/adaptive_issuance_launch_cycle": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/attestation_branch": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "index",
      "next"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "big_map_id",
      "descr": "A big map identifier"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "contents",
      "key_type",
      "total_bytes",
      "value_type"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}/contents": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "script_expr",
      "descr": "script_expr (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}/contents/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}/key_type": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}/total_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/index/{}/value_type": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/big_maps/next": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/block_round": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/commitments": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "Blinded public key hash",
      "descr": "Blinded public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/commitments/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/consensus_keys": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/consensus_keys/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "global_counter",
      "index",
      "total_supply"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/global_counter": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "contract_id",
      "descr": "A contract identifier encoded in b58check."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "balance",
      "bond_id_index",
      "code",
      "consensus_key",
      "counter",
      "delegate",
      "delegate_desactivation",
      "delegated",
      "frozen_deposits_limit",
      "frozen_deposits_pseudotokens",
      "inactive_delegate",
      "manager",
      "missed_attestations",
      "paid_bytes",
      "staking_parameters",
      "staking_pseudotokens",
      "storage",
      "total_frozen_bonds",
      "unstake_requests",
      "unstaked_frozen_deposits",
      "used_bytes"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/balance": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/bond_id_index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "bond_id",
      "descr": "A bond identifier."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/bond_id_index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "frozen_bonds"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/bond_id_index/{}/frozen_bonds": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/code": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/consensus_key": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "active"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/consensus_key/active": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/counter": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/delegate": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/delegate_desactivation": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/delegated": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "contract_id",
      "descr": "A contract identifier encoded in b58check."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/delegated/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/frozen_deposits_limit": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/frozen_deposits_pseudotokens": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/inactive_delegate": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/manager": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/missed_attestations": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/paid_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/staking_parameters": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "active"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/staking_parameters/active": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/staking_pseudotokens": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/storage": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/total_frozen_bonds": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/unstake_requests": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/unstaked_frozen_deposits": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/index/{}/used_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/contracts/total_supply": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_cycle",
      "descr": "A cycle integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "already_denounced",
      "delegate_sampler_state",
      "issuance_bonus",
      "issuance_coeff",
      "nonces",
      "pending_consensus_keys",
      "pending_staking_parameters",
      "random_seed",
      "selected_stake_distribution",
      "total_active_stake"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/already_denounced": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/already_denounced/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_round",
      "descr": "A round integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/already_denounced/{}/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/already_denounced/{}/{}/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/delegate_sampler_state": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/issuance_bonus": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/issuance_coeff": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/nonces": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/nonces/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/pending_consensus_keys": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "contract_id",
      "descr": "A contract identifier encoded in b58check."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/pending_consensus_keys/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/pending_staking_parameters": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "contract_id",
      "descr": "A contract identifier encoded in b58check."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/pending_staking_parameters/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/random_seed": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/selected_stake_distribution": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/cycle/{}/total_active_stake": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/dal": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "level",
      "slot_headers_history"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/dal/level": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/dal/level/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "slot_headers"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/dal/level/{}/slot_headers": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/dal/slot_headers_history": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/delegates": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/delegates/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/denunciations": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/denunciations/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/first_level_of_protocol": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/forbidden_delegates": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/global_constant": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "script_expr",
      "descr": "script_expr (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/global_constant/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/grand_parent_branch": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/liquidity_baking_cpmm_address": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/liquidity_baking_escape_ema": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/pending_migration_balance_updates": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/pending_migration_operation_results": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ramp_up": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "rewards"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/ramp_up/rewards": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_cycle",
      "descr": "A cycle integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ramp_up/rewards/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "index",
      "next"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_state_id",
      "descr": "A sapling state identifier"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "ciphertexts",
      "commitments",
      "commitments_size",
      "memo_size",
      "nullifiers_hashed",
      "nullifiers_ordered",
      "nullifiers_size",
      "roots",
      "roots_level",
      "roots_pos",
      "total_bytes"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/ciphertexts": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_ciphertext_position",
      "descr": "The position of a sapling ciphertext"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/ciphertexts/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/commitments": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_node_position",
      "descr": "The position of a node in a sapling commitment tree"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/commitments/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/commitments_size": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/memo_size": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/nullifiers_hashed": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_nullifier",
      "descr": "A sapling nullifier"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/nullifiers_hashed/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/nullifiers_ordered": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_nullifier_position",
      "descr": "A sapling nullifier position"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/nullifiers_ordered/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/nullifiers_size": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/roots": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "sapling_root",
      "descr": "A sapling root"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/roots/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/roots_level": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/roots_pos": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/index/{}/total_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/sapling/next": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/seed_status": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/slashed_deposits": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/slashed_deposits/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "inbox",
      "index",
      "past_commitment_periods"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/inbox": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "smart_rollup_address",
      "descr": "smart_rollup_address (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "commitment_added",
      "commitment_first_publication_level",
      "commitment_index",
      "commitments",
      "commitments_per_inbox_level",
      "commitments_stakers",
      "game",
      "game_timeout",
      "genesis_info",
      "kind",
      "last_cemented_commitment",
      "last_whitelist_update",
      "level_index",
      "parameters_type",
      "refutation_game_info",
      "staker_index",
      "staker_index_counter",
      "stakers",
      "whitelist",
      "whitelist_paid_bytes",
      "whitelist_use_bytes"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitment_added": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "smart_rollup_commitment_hash",
      "descr": "smart_rollup_commitment_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitment_added/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitment_first_publication_level": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitment_first_publication_level/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitment_index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "smart_rollup_commitment_hash",
      "descr": "smart_rollup_commitment_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments_per_inbox_level": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "block_level",
      "descr": "A level integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments_per_inbox_level/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments_stakers": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "smart_rollup_commitment_hash",
      "descr": "smart_rollup_commitment_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/commitments_stakers/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "opponents"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game/{}/opponents": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game/{}/opponents/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game_timeout": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "game_index",
      "descr": "A pair of stakers that index a smart rollup refutation game."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/game_timeout/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/genesis_info": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/kind": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/last_cemented_commitment": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/last_whitelist_update": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/level_index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "level_index",
      "descr": "The level index for applied outbox message records"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/level_index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "applied_outbox_messages"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/level_index/{}/applied_outbox_messages": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/parameters_type": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/refutation_game_info": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "game_index",
      "descr": "A pair of stakers that index a smart rollup refutation game."
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/refutation_game_info/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/staker_index": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/staker_index/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/staker_index_counter": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/stakers": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "z",
      "descr": "\u00af\\_(\u30c4)_/\u00af"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/stakers/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/whitelist": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/whitelist/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/whitelist_paid_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/index/{}/whitelist_use_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/smart_rollup/past_commitment_periods": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/staking_balance": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/staking_balance/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ticket_balance": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "paid_bytes",
      "table",
      "used_bytes"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/ticket_balance/paid_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ticket_balance/table": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "script_expr",
      "descr": "script_expr (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ticket_balance/table/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/ticket_balance/used_bytes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/vdf_challenge": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "ballots",
      "current_period",
      "current_proposal",
      "listings",
      "participation_ema",
      "pred_period_kind",
      "proposals",
      "proposals_count",
      "voting_power_in_listings"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/ballots": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/ballots/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/current_period": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/current_proposal": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/listings": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/listings/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/participation_ema": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/pred_period_kind": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/proposals": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "Protocol_hash",
      "descr": "Protocol_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/proposals/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/proposals/{}/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Boolean"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/proposals_count": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "pkh",
      "descr": "A Secp256k1 of a Ed25519 public key hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/proposals_count/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Integer"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/votes/voting_power_in_listings": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "String"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "Zk_rollup_hash",
      "descr": "Zk_rollup_hash (Base58Check-encoded)"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    },
    "props": [
      "account",
      "pending_list",
      "pending_operations"
    ]
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup/{}/account": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup/{}/pending_list": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Object"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup/{}/pending_operations": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    },
    "item": {
      "name": "zkru_pending_op_position",
      "descr": "The position of an operation in a pending operations list"
    }
  },
  "/chains/{}/blocks/{}/context/raw/json/zk_rollup/{}/pending_operations/{}": {
    "GET": {
      "descr": "\u00af\\_(\u30c4)_/\u00af",
      "args": [
        {
          "name": "depth",
          "descr": "\u00af\\_(\u30c4)_/\u00af"
        }
      ],
      "ret": "Array"
    }
  }
}
