docs = {   'ABS': 'ABS\nABS :: int : A => nat : A\nObtain the absolute value of an integer',
    'ADD': 'ADD\n'
           'ADD :: nat : nat : A => nat : A\n'
           'ADD :: nat : int : A => int : A\n'
           'ADD :: int : nat : A => int : A\n'
           'ADD :: int : int : A => int : A\n'
           'ADD :: timestamp : int : A => timestamp : A\n'
           'ADD :: int : timestamp : A => timestamp : A\n'
           'ADD :: mutez : mutez : A => mutez : A\n'
           'ADD :: bls12_381_g1 : bls12_381_g1 : A => bls12_381_g1 : A\n'
           'ADD :: bls12_381_g2 : bls12_381_g2 : A => bls12_381_g2 : A\n'
           'ADD :: bls12_381_fr : bls12_381_fr : A => bls12_381_fr : A\n'
           'Add two numerical values',
    'ADDRESS': 'ADDRESS\nADDRESS :: contract ty1 : A => address : A\nCast a typed address to an untyped address',
    'AMOUNT': 'AMOUNT\nAMOUNT :: A => mutez : A\nPush the amount of the current transaction',
    'AND': 'AND\n'
           'AND :: bool : bool : A => bool : A\n'
           'AND :: nat : nat : A => nat : A\n'
           'AND :: int : nat : A => nat : A\n'
           'AND :: bytes : bytes : A => bytes : A\n'
           'Boolean and bitwise AND',
    'APPLY': 'APPLY\n'
             'APPLY :: ty1 : lambda ( pair ty1 ty2 ) ty3 : A => lambda ty2 ty3 : A\n'
             'Partially apply a tuplified function from the stack',
    'BALANCE': 'BALANCE\nBALANCE :: A => mutez : A\nPush the current amount of mutez of the executing contract',
    'BLAKE2B': 'BLAKE2B\nBLAKE2B :: bytes : A => bytes : A\nCompute a Blake2B cryptographic hash',
    'BYTES': 'BYTES\n'
             'BYTES :: int : A => bytes : A\n'
             'BYTES :: nat : A => bytes : A\n'
             'Encode an integer or a natural number to bytes',
    'CAR': 'CAR\nCAR :: pair ty1 ty2 : A => ty1 : A\nAccess the left part of a pair',
    'CAST': '',
    'CDR': 'CDR\nCDR :: pair ty1 ty2 : A => ty2 : A\nAccess the right part of a pair',
    'CHAIN_ID': 'CHAIN_ID\nCHAIN_ID :: A => chain_id : A\nPush the chain identifier',
    'CHECK_SIGNATURE': 'CHECK_SIGNATURE\n'
                       'CHECK_SIGNATURE :: key : signature : bytes : A => bool : A\n'
                       'Verify signature of bytes by key',
    'COMPARE': 'COMPARE\nCOMPARE :: cty : cty : A => int : A\nCompare two values',
    'CONCAT': 'CONCAT\n'
              'CONCAT :: string : string : A => string : A\n'
              'CONCAT :: list string : A => string : A\n'
              'CONCAT :: bytes : bytes : A => bytes : A\n'
              'CONCAT :: list bytes : A => bytes : A\n'
              'Concatenate strings or byte sequences',
    'CONS': 'CONS\nCONS :: ty1 : list ty1 : A => list ty1 : A\nPrepend an element to a list',
    'CONTRACT': 'CONTRACT ty\n'
                'CONTRACT ty :: address : A => option ( contract ty ) : A\n'
                'Cast an address to a typed address',
    'CREATE_ACCOUNT': '\nPush an account creation operation',
    'CREATE_CONTRACT': 'CREATE_CONTRACT { parameter ty1 ; storage ty2 ; code instr1 }\n'
                       'CREATE_CONTRACT { parameter ty1 ; storage ty2 ; code instr1 } :: option key_hash : mutez : ty2 '
                       ': A => operation : address : A\n'
                       'Push a contract creation operation',
    'DIG': 'DIG n\nDIG n :: A @ ( ty1 : B ) => ty1 : ( A @ B )\nRetrieve the n\\ th element of the stack',
    'DIP': 'DIP instr\nDIP instr :: ty : B => ty : C\nRun code protecting the top of the stack',
    'DIPN': 'DIP n instr\nDIP n instr :: A @ B => A @ C\nRun code protecting the n topmost elements of the stack',
    'DROP': 'DROP\nDROP :: ty : A => A\nDrop the top element of the stack',
    'DROPN': 'DROP n\nDROP n :: A @ B => B\nDrop the top n elements of the stack',
    'DUG': 'DUG n\nDUG n :: ty1 : ( A @ B ) => A @ ( ty1 : B )\nInsert the top element at depth n',
    'DUP': 'DUP\nDUP :: ty1 : A => ty1 : ty1 : A\nDuplicate the top of the stack',
    'DUPN': 'DUP n\nDUP n :: A @ ty1 : B => ty1 : A @ ty1 : B\nDuplicate the n\\ th element of the stack',
    'EDIV': 'EDIV\n'
            'EDIV :: nat : nat : A => option ( pair nat nat ) : A\n'
            'EDIV :: nat : int : A => option ( pair int nat ) : A\n'
            'EDIV :: int : nat : A => option ( pair int nat ) : A\n'
            'EDIV :: int : int : A => option ( pair int nat ) : A\n'
            'EDIV :: mutez : nat : A => option ( pair mutez mutez ) : A\n'
            'EDIV :: mutez : mutez : A => option ( pair nat mutez ) : A\n'
            'Euclidean division',
    'EMIT': 'EMIT ty\nEMIT ty :: ty : A => operation : A\nWrite an event into the transaction receipt',
    'EMPTY_BIG_MAP': 'EMPTY_BIG_MAP kty vty\n'
                     'EMPTY_BIG_MAP kty vty :: A => big_map kty vty : A\n'
                     'Build a new, empty big_map from kty to vty',
    'EMPTY_MAP': 'EMPTY_MAP kty vty\nEMPTY_MAP kty vty :: A => map kty vty : A\nBuild a new, empty map from kty to vty',
    'EMPTY_SET': 'EMPTY_SET cty\nEMPTY_SET cty :: A => set cty : A\nBuild a new, empty set for elements of type cty',
    'EQ': 'EQ\nEQ :: int : A => bool : A\nCheck that the top of the stack equals zero',
    'EXEC': 'EXEC\nEXEC :: ty1 : lambda ty1 ty2 : A => ty2 : A\nExecute a function from the stack',
    'EXPAND': '',
    'FAILWITH': 'FAILWITH\nFAILWITH :: ty1 : A => B\nExplicitly abort the current program',
    'GE': 'GE\nGE :: int : A => bool : A\nCheck that the top of the stack is greater than or equal to zero',
    'GET': 'GET\n'
           'GET :: kty : map kty vty : A => option vty : A\n'
           'GET :: kty : big_map kty vty : A => option vty : A\n'
           'Access an element in a map or big_map',
    'GETN': 'GET n\n'
            'GET 0 :: ty : A => ty : A\n'
            'GET 1 :: pair ty1 ty2 : A => ty1 : A\n'
            'GET ( n + 2 ) :: pair ty1 ty2 : A => ty : A\n'
            'Access an element or a sub comb in a right comb',
    'GET_AND_UPDATE': 'GET_AND_UPDATE\n'
                      'GET_AND_UPDATE :: kty : option vty : map kty vty : A => option vty : map kty vty : A\n'
                      'GET_AND_UPDATE :: kty : option vty : big_map kty vty : A => option vty : big_map kty vty : A\n'
                      'A combination of the GET and UPDATE instructions',
    'GT': 'GT\nGT :: int : A => bool : A\nCheck that the top of the stack is greater than zero',
    'HASH_KEY': 'HASH_KEY\nHASH_KEY :: key : A => key_hash : A\nCompute the Base58Check of a public key',
    'IF': 'IF instr1 instr2\nIF instr1 instr2 :: bool : A => B\nConditional branching',
    'IF_CONS': 'IF_CONS instr1 instr2\nIF_CONS instr1 instr2 :: list ty : A => B\nInspect a list',
    'IF_LEFT': 'IF_LEFT instr1 instr2\nIF_LEFT instr1 instr2 :: or ty1 ty2 : A => B\nInspect a value of a union',
    'IF_NONE': 'IF_NONE instr1 instr2\nIF_NONE instr1 instr2 :: option ty1 : A => B\nInspect an optional value',
    'IMPLICIT_ACCOUNT': 'IMPLICIT_ACCOUNT\n'
                        'IMPLICIT_ACCOUNT :: key_hash : A => contract unit : A\n'
                        'Convert a key hash to a typed address',
    'INT': 'INT\n'
           'INT :: nat : A => int : A\n'
           'INT :: bls12_381_fr : A => int : A\n'
           'INT :: bytes : A => int : A\n'
           'Convert a natural number, a BLS12-381 field element, or a byte sequence to an integer',
    'ISNAT': 'ISNAT\nISNAT :: int : A => option nat : A\nConvert a non-negative integer to a natural number',
    'IS_IMPLICIT_ACCOUNT': 'IS_IMPLICIT_ACCOUNT\n'
                           'IS_IMPLICIT_ACCOUNT :: address : A => option key_hash : A\n'
                           'Cast an address to a public key hash',
    'ITER': 'ITER instr\n'
            'ITER instr :: list ty : A => A\n'
            'ITER instr :: set cty : A => A\n'
            'ITER instr :: map kty vty : A => A\n'
            'Iterate over a set, list or map',
    'JOIN_TICKETS': 'JOIN_TICKETS\n'
                    'JOIN_TICKETS :: pair ( ticket cty ) ( ticket cty ) : A => option ( ticket cty ) : A\n'
                    'Join two tickets into one',
    'KECCAK': 'KECCAK\nKECCAK :: bytes : A => bytes : A\nCompute a Keccak-256 cryptographic hash',
    'LAMBDA': 'LAMBDA ty1 ty2 instr\nLAMBDA ty1 ty2 instr :: A => lambda ty1 ty2 : A\nPush a lambda onto the stack',
    'LAMBDA_REC': 'LAMBDA_REC ty1 ty2 instr\n'
                  'LAMBDA_REC ty1 ty2 instr :: A => lambda ty1 ty2 : A\n'
                  'Push a recursive lambda onto the stack',
    'LE': 'LE\nLE :: int : A => bool : A\nCheck that the top of the stack is less than or equal to zero',
    'LEFT': 'LEFT ty2\nLEFT ty2 :: ty1 : A => or ty1 ty2 : A\nWrap a value in a union (left case)',
    'LEVEL': 'LEVEL\nLEVEL :: A => nat : A\nPush the current block level',
    'LOOP': 'LOOP instr\nLOOP instr :: bool : A => A\nA generic loop',
    'LOOP_LEFT': 'LOOP_LEFT instr\nLOOP_LEFT instr :: or ty1 ty2 : A => ty2 : A\nLoop with accumulator',
    'LSL': 'LSL\n'
           'LSL :: nat : nat : A => nat : A\n'
           'LSL :: bytes : nat : A => bytes : A\n'
           'Logically left shift of a natural number or of a byte sequence',
    'LSR': 'LSR\n'
           'LSR :: nat : nat : A => nat : A\n'
           'LSR :: bytes : nat : A => bytes : A\n'
           'Logically right shift of a natural number or of a byte sequence',
    'LT': 'LT\nLT :: int : A => bool : A\nCheck that the top of the stack is less than zero',
    'MAP': 'MAP instr\n'
           'MAP instr :: list ty : A => list ty2 : A\n'
           'MAP instr :: option ty : A => option ty2 : A\n'
           'MAP instr :: map kty ty1 : A => map kty ty2 : A\n'
           'Apply instr to each element of a list, an option, or map.',
    'MEM': 'MEM\n'
           'MEM :: cty : set cty : A => bool : A\n'
           'MEM :: kty : map kty vty : A => bool : A\n'
           'MEM :: kty : big_map kty vty : A => bool : A\n'
           'Check for the presence of a binding for a key in a map, set or big_map',
    'MIN_BLOCK_TIME': 'MIN_BLOCK_TIME\nMIN_BLOCK_TIME :: A => nat : A\nPush the current minimal block time in seconds.',
    'MUL': 'MUL\n'
           'MUL :: nat : nat : A => nat : A\n'
           'MUL :: nat : int : A => int : A\n'
           'MUL :: int : nat : A => int : A\n'
           'MUL :: int : int : A => int : A\n'
           'MUL :: mutez : nat : A => mutez : A\n'
           'MUL :: nat : mutez : A => mutez : A\n'
           'MUL :: bls12_381_g1 : bls12_381_fr : A => bls12_381_g1 : A\n'
           'MUL :: bls12_381_g2 : bls12_381_fr : A => bls12_381_g2 : A\n'
           'MUL :: bls12_381_fr : bls12_381_fr : A => bls12_381_fr : A\n'
           'MUL :: nat : bls12_381_fr : A => bls12_381_fr : A\n'
           'MUL :: int : bls12_381_fr : A => bls12_381_fr : A\n'
           'MUL :: bls12_381_fr : nat : A => bls12_381_fr : A\n'
           'MUL :: bls12_381_fr : int : A => bls12_381_fr : A\n'
           'Multiply two numerical values',
    'NAT': 'NAT\nNAT :: bytes : A => nat : A\nConvert bytes to a natural number',
    'NEG': 'NEG\n'
           'NEG :: nat : A => int : A\n'
           'NEG :: int : A => int : A\n'
           'NEG :: bls12_381_g1 : A => bls12_381_g1 : A\n'
           'NEG :: bls12_381_g2 : A => bls12_381_g2 : A\n'
           'NEG :: bls12_381_fr : A => bls12_381_fr : A\n'
           'Negate a numerical value',
    'NEQ': 'NEQ\nNEQ :: int : A => bool : A\nCheck that the top of the stack is not equal to zero',
    'NEVER': 'NEVER\nNEVER :: never : A => B\nClose a forbidden branch',
    'NIL': 'NIL ty\nNIL ty :: A => list ty : A\nPush an empty list',
    'NONE': 'NONE ty\nNONE ty :: A => option ty : A\nPush the absent optional value',
    'NOOP': '{}\n{} :: A => A\nEmpty instruction sequence',
    'NOT': 'NOT\n'
           'NOT :: bool : A => bool : A\n'
           'NOT :: nat : A => int : A\n'
           'NOT :: int : A => int : A\n'
           'NOT :: bytes : A => bytes : A\n'
           'Boolean negation and bitwise complement',
    'NOW': 'NOW\nNOW :: A => timestamp : A\nPush block timestamp',
    'OPEN_CHEST': 'OPEN_CHEST\n'
                  'OPEN_CHEST :: chest_key : chest : nat : A => option bytes : A\n'
                  'Open a timelocked chest given its key and the time',
    'OR': 'OR\n'
          'OR :: bool : bool : A => bool : A\n'
          'OR :: nat : nat : A => nat : A\n'
          'OR :: bytes : bytes : A => bytes : A\n'
          'Boolean and bitwise OR',
    'PACK': 'PACK\nPACK :: ty : A => bytes : A\nSerialize data',
    'PAIR': "PAIR\nPAIR :: ty1 : ty2 : A => pair ty1 ty2 : A\nBuild a pair from the stack's top two elements",
    'PAIRING_CHECK': 'PAIRING_CHECK\n'
                     'PAIRING_CHECK :: list ( pair bls12_381_g1 bls12_381_g2 ) : A => bool : A\n'
                     'Check a BLS12-381 pairing',
    'PAIRN': 'PAIR n\n'
             'PAIR n :: ty1 : .... : tyN : A => pair ty1 .... tyN : A\n'
             'Fold n values on the top of the stack into a right comb',
    'PUSH': 'PUSH ty x\nPUSH ty x :: A => ty : A\nPush a constant value of a given type onto the stack',
    'READ_TICKET': 'READ_TICKET\n'
                   'READ_TICKET :: ticket cty : A => pair address cty nat : ticket cty : A\n'
                   'Retrieve the information stored in a ticket. Also return the ticket.',
    'RENAME': '',
    'RIGHT': 'RIGHT ty1\nRIGHT ty1 :: ty2 : A => or ty1 ty2 : A\nWrap a value in a union (right case)',
    'SAPLING_EMPTY_STATE': 'SAPLING_EMPTY_STATE ms\n'
                           'SAPLING_EMPTY_STATE ms :: A => sapling_state ms : A\n'
                           'Push an empty Sapling state on the stack',
    'SAPLING_VERIFY_UPDATE': 'SAPLING_VERIFY_UPDATE\n'
                             'SAPLING_VERIFY_UPDATE :: sapling_transaction ms : sapling_state ms : A => option ( pair '
                             'bytes ( pair int ( sapling_state ms ) ) ) : A\n'
                             'Verify and apply a transaction on a Sapling state',
    'SELF': 'SELF\nSELF :: A => contract ty : A\nPush the current contract',
    'SELF_ADDRESS': 'SELF_ADDRESS\nSELF_ADDRESS :: A => address : A\nPush the address of the current contract',
    'SENDER': 'SENDER\nSENDER :: A => address : A\nPush the address that directly initiated the current transaction',
    'SEQ': 'instr1 ; instr2\ninstr1 ; instr2 :: A => C\nInstruction sequence',
    'SET_DELEGATE': 'SET_DELEGATE\nSET_DELEGATE :: option key_hash : A => operation : A\nPush a delegation operation',
    'SHA256': 'SHA256\nSHA256 :: bytes : A => bytes : A\nCompute a SHA-256 cryptographic hash',
    'SHA3': 'SHA3\nSHA3 :: bytes : A => bytes : A\nCompute a SHA3-256 cryptographic hash',
    'SHA512': 'SHA512\nSHA512 :: bytes : A => bytes : A\nCompute a SHA-512 cryptographic hash',
    'SIZE': 'SIZE\n'
            'SIZE :: set cty : A => nat : A\n'
            'SIZE :: map kty vty : A => nat : A\n'
            'SIZE :: list ty : A => nat : A\n'
            'SIZE :: string : A => nat : A\n'
            'SIZE :: bytes : A => nat : A\n'
            'Obtain size of a string, list, set, map or byte sequence bytes',
    'SLICE': 'SLICE\n'
             'SLICE :: nat : nat : string : A => option string : A\n'
             'SLICE :: nat : nat : bytes : A => option bytes : A\n'
             'Obtain a substring or subsequence of a string respectively byte sequence bytes',
    'SOME': 'SOME\nSOME :: ty1 : A => option ty1 : A\nWrap an existing optional value',
    'SOURCE': 'SOURCE\n'
              'SOURCE :: A => address : A\n'
              'Push the address that directly or indirectly initiated the current transaction',
    'SPLIT_TICKET': 'SPLIT_TICKET\n'
                    'SPLIT_TICKET :: ticket cty : pair nat nat : A => option ( pair ( ticket cty ) ( ticket cty ) ) : '
                    'A\n'
                    'Split a ticket in two',
    'STEPS_TO_QUOTA': '\nPush the remaining steps before the contract execution must terminate',
    'SUB': 'SUB\n'
           'SUB :: nat : nat : A => int : A\n'
           'SUB :: nat : int : A => int : A\n'
           'SUB :: int : nat : A => int : A\n'
           'SUB :: int : int : A => int : A\n'
           'SUB :: timestamp : int : A => timestamp : A\n'
           'SUB :: timestamp : timestamp : A => int : A\n'
           'Subtract two numerical values',
    'SUB_MUTEZ': 'SUB_MUTEZ\nSUB :: mutez : mutez : A => option mutez : A\nSubtract two mutez',
    'SWAP': 'SWAP\nSWAP :: ty1 : ty2 : A => ty2 : ty1 : A\nSwap the top two elements of the stack',
    'TICKET': 'TICKET\nTICKET :: cty : nat : A => option ( ticket cty ) : A\nCreate a ticket',
    'TOP': '',
    'TOTAL_VOTING_POWER': 'TOTAL_VOTING_POWER\n'
                          'TOTAL_VOTING_POWER :: A => nat : A\n'
                          'Return the total voting power of all delegates',
    'TRANSFER_TOKENS': 'TRANSFER_TOKENS\n'
                       'TRANSFER_TOKENS :: ty : mutez : contract ty : A => operation : A\n'
                       'Push a transaction operation',
    'UNIT': 'UNIT\nUNIT :: A => unit : A\nPush the unit value onto the stack',
    'UNPACK': 'UNPACK ty\nUNPACK ty :: bytes : A => option ty : A\nDeserialize data, if valid',
    'UNPAIR': 'UNPAIR\nUNPAIR :: pair ty1 ty2 : A => ty1 : ty2 : A\nSplit a pair into its components',
    'UNPAIRN': 'UNPAIR n\n'
               'UNPAIR n :: pair ty1 .... tyN : A => ty1 : .... : tyN : A\n'
               'Unfold n values from a right comb on the top of the stack',
    'UPDATE': 'UPDATE\n'
              'UPDATE :: cty : bool : set cty : A => set cty : A\n'
              'UPDATE :: kty : option vty : map kty vty : A => map kty vty : A\n'
              'UPDATE :: kty : option vty : big_map kty vty : A => big_map kty vty : A\n'
              'Add, update, or remove an element in a map, big_map or set',
    'UPDATEN': 'UPDATE n\n'
               'UPDATE 0 :: ty1 : ty2 : A => ty1 : A\n'
               'UPDATE 1 :: ty : pair ty1 ty2 : A => pair ty ty2 : A\n'
               "UPDATE ( n + 2 ) :: ty : pair ty1 ty2 : A => pair ty1 ty' : A\n"
               'Update an element or a sub comb in a right comb',
    'VIEW': 'VIEW name return_ty\nVIEW name return_ty :: ty : address : A => option return_ty : A\nCall a view',
    'VOTING_POWER': 'VOTING_POWER\nVOTING_POWER :: key_hash : A => nat : A\nReturn the voting power of a given account',
    'XOR': 'XOR\n'
           'XOR :: bool : bool : A => bool : A\n'
           'XOR :: nat : nat : A => nat : A\n'
           'XOR :: bytes : bytes : A => bytes : A\n'
           'Boolean and bitwise eXclusive OR',
    'address': 'address\nUntyped address of a smart contract, account, or rollup',
    'big_map': 'big_map kty vty\nA lazily deserialized map from kty to vty',
    'bls12_381_fr': 'bls12_381_fr\nAn element of the BLS12-381 scalar field F\\ :sub:r',
    'bls12_381_g1': 'bls12_381_g1\nA point on the BLS12-381 curve G\\ :sub:1',
    'bls12_381_g2': 'bls12_381_g2\nA point on the BLS12-381 curve G\\ :sub:2',
    'bool': 'bool\nA boolean',
    'bytes': 'bytes\nA sequence of bytes',
    'chain_id': 'chain_id\nA chain identifier',
    'chest': 'chest\nA timelocked chest',
    'chest_key': 'chest_key\nA key to open a timelocked chest',
    'contract': 'contract type\nAddress of a smart contract, account, or rollup, where type is the parameter type',
    'int': 'int\nAn arbitrary-precision integer',
    'key': 'key\nA public cryptographic key',
    'key_hash': 'key_hash\nA hash of a public cryptographic key',
    'lambda': 'lambda ty1 ty2\nA lambda with given parameter and return types',
    'list': 'list type\nA single, immutable, homogeneous linked list',
    'map': 'map kty vty\nAn immutable map from kty to vty',
    'mutez': 'mutez\nA specific type for manipulating tokens',
    'nat': 'nat\nAn arbitrary-precision natural number',
    'never': 'never\nThe empty type',
    'operation': 'operation\nAn internal operation emitted by a contract',
    'option': 'option ty\nAn optional value',
    'or': 'or ty1 ty2\nA union of two types',
    'pair': 'pair ty1 ty2\nA pair or tuple of values',
    'sapling_state': 'sapling_state n\nA Sapling state',
    'sapling_transaction': 'sapling_transaction n\nA Sapling transaction',
    'set': 'set cty\nAn immutable set of comparable values of type cty',
    'signature': 'signature\nA cryptographic signature',
    'string': 'string\nA string of characters',
    'ticket': 'ticket cty\nA ticket used to authenticate information of type cty',
    'timestamp': 'timestamp\nA real-world date.',
    'unit': 'unit\nThe type whose only value is Unit'}
