define([
    'codemirror/lib/codemirror',
    'codemirror/addon/mode/simple'
], function(CodeMirror) {
     var onload = function() {
        CodeMirror.defineSimpleMode("michelson", {
            start: [
                // delimiters
                { regex: /[;\{\(\s]/, token: "variable", next: "start" },
                // string
                { regex: /"(?:[^\\]|\\.)*?(?:"|$)/, token: "string" },
                // bytes
                { regex: /(?:0x[0-9a-f]+)(?=\s|;|\}|\)|$)/i, token: "string" },
                // int
                { regex: /(?:[+-]?[0-9]+\.?[0-9]*)(?=\s|;|\}|\)|$)/, token: "string" },
                // comment
                { regex: /#.*/, token: "comment" },
                { regex: /\/\*/, token: "comment", next: "comment" },
                // block
                { regex: /(?:parameter|storage|code)(?=\s|$)/, token: "keyword" },
                // data
                { regex: /(?:Unit|True|False|Pair|Left|Right|Some|None|Elt)(?=\s|;|\)|$)/, token: "keyword" },
                // instruction
                { regex: /(?:INT|ISNAT|NAT|BYTES|CAST|RENAME|DROP|DUP|SWAP|PUSH|SOME|NONE|UNIT|IF_NONE|PAIR|CAR|CDR|LEFT|RIGHT|IF_LEFT|IF_RIGHT|NIL|CONS|IF_CONS|SIZE|EMPTY_SET|EMPTY_MAP|MAP|ITER|MEM|GET|UPDATE|IF|LOOP|LOOP_LEFT|LAMBDA|EXEC|DIP|FAILWITH|CONCAT|SLICE|PACK|UNPACK|ADD|SUB|MUL|EDIV|ABS|NEG|LSL|LSR|OR|AND|XOR|NOT|COMPARE|EQ|NEQ|LT|GT|LE|GE|CHECK_SIGNATURE|BLAKE2B|SHA256|SHA512|HASH_KEY|DIG|DUG|EMPTY_BIG_MAP|APPLY|NEVER|UNPAIR|VOTING_POWER|KECCAK|SHA3|PAIRING_CHECK|SAPLING_VERIFY_UPDATE|TICKET|READ_TICKET|SPLIT_TICKET|JOIN_TICKETS|GET_AND_UPDATE|IS_IMPLICIT_ACCOUNT)(?=\s|;|\}|$)/, token: "meta"},
                { regex: /(?:SELF|CONTRACT|TRANSFER_TOKENS|SET_DELEGATE|CREATE_CONTRACT|IMPLICIT_ACCOUNT|NOW|AMOUNT|BALANCE|STEPS_TO_QUOTA|SOURCE|SENDER|ADDRESS|CHAIN_ID|LEVEL|SELF_ADDRESS|TOTAL_VOTING_POWER|SAPLING_EMPTY_STATE|MIN_BLOCK_TIME)(?=\s|;|\}|$)/, token: "operator"},
                // type
                { regex: /(?:option|list|set|contract|pair|or|lambda|map|big_map)(?=\s|\)|$)/, token: "builtin" },
                { regex: /(?:key|unit|signature|operation|address|int|nat|string|bytes|mutez|bool|key_hash|timestamp|chain_id|never|bls12_381_g1|bls12_381_g2|bls12_381_fr|sapling_state|sapling_transaction|sapling_transaction_deprecated|tx_rollup_l2_address)(?=\s|\)|\}|;|$)/, token: "builtin" },
                // macros
                { regex: /(?:IF_SOME|FAIL|ASSERT|ASSERT_NONE|ASSERT_SOME|ASSERT_LEFT|ASSERT_RIGHT|UNPAIR|(?:SET|MAP)_C[AD]+R)(?=\s|;|\}|$)/, token: "string-2" },
                { regex: /(?:DII+P|C[AD]{2,}R|DUU+P|P[PAI]{3,}R|UNP[PAI]{3,}R)(?=\s|;|\}|$)/, token: "string-2" },
                { regex: /(?:(?:CMP|IF|IFCMP|ASSERT_|ASSERT_CMP)(?:EQ|NEQ|LT|GT|LE|GE))(?=\s|;|\}|\{|$)/, token: "string-2" },
                // annotations
                { regex: /(?:%[A-z_0-9%@]*)(?=\s|\)|\}|$)/, token: "atom" },
                { regex: /(?:@[A-z_0-9%]+)(?=\s|\)|\}|$)/, token: "atom" },
                { regex: /(?::[A-z_0-9]+)(?=\s|\)|\}|$)/, token: "atom" },
                // helpers
                { regex: /(?:DUMP|PRINT|DROP_ALL|EXPAND|PATCH|INCLUDE|DEBUG|BIG_MAP_DIFF|BEGIN|COMMIT|RESET|STORAGE)(?=\s|;|\}|$)/, token: "def" },
                // fallback
                { regex: /[^\s]+/, token: "variable"}
            ],
            comment: [
                { regex: /.*?\*\//, token: "comment", next: "start" },
                { regex: /.*/, token: "comment" }
            ],
            meta: {
                dontIndentStates: ["comment"],
                lineComment: "#",
                blockCommentStart: "/*",
                blockCommentEnd: "*/"
            }
        });
        CodeMirror.defineMIME("text/x-michelson", "michelson");
        CodeMirror.modeInfo.push({
            ext: ["tz"],
            mime: "text/x-michelson",
            mode: "michelson",
            name: "Michelson"
        });

        // Force mode on refresh
        // Big thanks to https://github.com/kelvich for this solution
        IPython.CodeCell.options_default["cm_config"]["mode"] = "michelson";
        [...document.querySelectorAll('.code_cell .CodeMirror')].forEach(c => {
            c.CodeMirror.setOption('mode', 'michelson');
        });
        Jupyter.notebook.get_cells().forEach(function(c) {
            if (c.cell_type == "code") {
                c._options.cm_config['mode'] = 'michelson';
            }
            else if (c.cell_type == "markdown") {
                c.unrender();
                c.render();
            }
        });
    }
    return { onload: onload }
});