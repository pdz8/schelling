
binDjBallot = \
"0x603261016061090b60043960045160245160445160645160845160a45160c45160e4516101045161012451610144516040565b610825806100e66000396000f35b8a6000819055508960028190555088600381905550876004819055508660045401600581905550856005540160068190555033600181905550846007600060058110608757005b0181905550836007600160058110609a57005b018190555082600760026005811060ad57005b018190555081600760036005811060c057005b018190555080600760046005811060d357005b01819055505050505050505050505050560060003560e060020a900480630441a875146100f757806312fdc8311461010b578063215adde21461012557806326bda3e014610137578063332beb88146101595780633b2d7c00146101675780633f66c090146101995780634553be6b146101ab57806346334697146101bc5780635079f9c3146101ce5780638e5dcdf5146101e057806395bb5227146101ee578063d693632514610200578063df29dfc414610217578063e369885314610229576100f16005544210156100c0576100c5565b6100ef565b34600c600032600160a060020a031681526020019081526020016000206003019081540190819055505b565b60006000f35b61010560043560243561057e565b60006000f35b61011f60043560243560443560643561032f565b60006000f35b61012d610771565b8060005260206000f35b61013f6107ad565b846000528360205282604052816060528060805260a06000f35b610161610244565b60006000f35b61019360043560243560443560643560843560a43560c43560e435610104356101243561014435610237565b60006000f35b6101a1610799565b8060005260206000f35b6101b660043561026c565b60006000f35b6101c461078f565b8060005260206000f35b6101d66107a3565b8060005260206000f35b6101e86105c9565b60006000f35b6101f6610785565b8060005260206000f35b61021160043560243560443561046a565b60006000f35b61021f61077b565b8060005260206000f35b610231610818565b60006000f35b5050505050505050505050565b33600f6000601054815260200190815260200160002081905550601080549081600101905550565b600060045442108061028057506005544210155b6102895761028e565b61032b565b329050600054600160a060020a031663573705a6602060008260e060020a02600052600485600160a060020a03168152602001600060008660155a03f1505050600051156102db576102e0565b61032b565b34600c600083600160a060020a0316815260200190815260200160002060030190815401908190555081600c600083600160a060020a03168152602001908152602001600020819055505b5050565b600060045442108061034357506005544210155b61034c57610351565b610463565b60016020600060008881526020018760ff168152602001868152602001858152602001600060008560155a03f150506000519050600154600160a060020a031632600160a060020a0316141580156103bb575032600160a060020a031681600160a060020a031614155b6103c4576103c9565b610463565b600054600160a060020a031663573705a6602060008260e060020a02600052600485600160a060020a03168152602001600060008660155a03f15050506000511561041357610418565b610463565b34600c600083600160a060020a0316815260200190815260200160002060030190815401908190555084600c600083600160a060020a03168152602001908152602001600020819055505b5050505050565b600060055442108061047e57506006544210155b6104875761048c565b610578565b826000148061049c575060025483115b6104a5576104aa565b610578565b600084600160a060020a0316606060020a02815260140130600160a060020a0316606060020a028152601401838152602001828152602001600020905080600c600032600160a060020a03168152602001908152602001600020541461050f57610577565b82600c600032600160a060020a0316815260200190815260200160002060010181905550601160008481526020019081526020016000208054908160010190555083600d6000600e54815260200190815260200160002081905550600e805490816001019055505b5b50505050565b30600160a060020a031663d6936325600060008260e060020a02600052600432600160a060020a03168152602001868152602001858152602001600060008660155a03f15050505050565b6000600060065442106105db576105e0565b61076d565b601254600014156105f0576105f5565b61076d565b6001915060006012819055505b6002548211610654576011600060125481526020019081526020016000205460116000848152602001908152602001600020541161063f57610647565b816012819055505b8180600101925050610602565b60125460001461066357610668565b61076d565b6011600060125481526020019081526020016000205430600160a060020a031631049050600091505b600e5482101561071157601254600c6000600d600086815260200190815260200160002054600160a060020a0316815260200190815260200160002060010154146106db5761070c565b600d600083815260200190815260200160002054600160a060020a03166000826000600060006000848787f1505050505b610691565b600091505b60105482101561076c57600f600083815260200190815260200160002054600160a060020a031663ed684cc6600060008260e060020a0260005260046012548152602001600060008660155a03f1505050610716565b5b5050565b6000600254905090565b6000600454905090565b6000600554905090565b6000600654905090565b6000600354905090565b6000601254905090565b6000600060006000600060076000600581106107c557005b0154945060076001600581106107d757005b0154935060076002600581106107e957005b0154925060076003600581106107fb57005b01549150600760046005811061080d57005b015490509091929394565b32600160a060020a0316ff56"

abiDjBallot = \
[{"constant" : False,"inputs" : [{"name" : "voteVal","type" : "uint256"},{"name" : "key","type" : "uint256"}],"name" : "reveal_hash","outputs" : [],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "h","type" : "hash256"},{"name" : "v","type" : "hash8"},{"name" : "r","type" : "hash256"},{"name" : "s","type" : "hash256"}],"name" : "submit_hash_for","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_max_option","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_question","outputs" : [{"name" : "ret_q0","type" : "string32"},{"name" : "ret_q1","type" : "string32"},{"name" : "ret_q2","type" : "string32"},{"name" : "ret_q3","type" : "string32"},{"name" : "ret_q4","type" : "string32"}],"type" : "function"},{"constant" : False,"inputs" : [],"name" : "wait_for_decision","outputs" : [],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "_pool","type" : "address"},{"name" : "_maxOption","type" : "uint256"},{"name" : "_downPayment","type" : "uint256"},{"name" : "_startTime","type" : "uint256"},{"name" : "_votingPeriod","type" : "uint256"},{"name" : "_revealPeriod","type" : "uint256"},{"name" : "_q0","type" : "string32"},{"name" : "_q1","type" : "string32"},{"name" : "_q2","type" : "string32"},{"name" : "_q3","type" : "string32"},{"name" : "_q4","type" : "string32"}],"name" : "constructor_sig","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_down_payment","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "h","type" : "hash256"}],"name" : "submit_hash","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_redeem_time","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_decision","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : False,"inputs" : [],"name" : "tally_up","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_reveal_time","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "a","type" : "address"},{"name" : "voteVal","type" : "uint256"},{"name" : "key","type" : "uint256"}],"name" : "reveal_vote_for","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [],"name" : "get_start_time","outputs" : [{"name" : "ret","type" : "uint256"}],"type" : "function"},{"constant" : False,"inputs" : [],"name" : "kill_me","outputs" : [],"type" : "function"}]

binIWait = \
"0x602780600c6000396000f30060003560e060020a90048063ed684cc614601557005b601e6004356024565b60006000f35b5056"

abiIWait = \
[{"constant" : False,"inputs" : [{"name" : "tval","type" : "uint256"}],"name" : "trigger","outputs" : [],"type" : "function"}]

binVoterPool = \
"0x60056013565b6103718061001d6000396000f35b33600081905550560060003560e060020a900480630a3b0a4f1461004d57806329092d0e1461005e578063573705a61461006f578063b9b4318d14610084578063c640752d146100a4578063e3698853146100b857005b6100586004356100c6565b60006000f35b610069600435610112565b60006000f35b61007a600435610315565b8060005260206000f35b61009e60043560243560443560643560843560a4356101cd565b60006000f35b6100b260043560243561015e565b60006000f35b6100c061033b565b60006000f35b600054600160a060020a031632600160a060020a031614156100e7576100ec565b61010f565b60016001600083600160a060020a03168152602001908152602001600020819055505b50565b600054600160a060020a031632600160a060020a0316141561013357610138565b61015b565b60006001600083600160a060020a03168152602001908152602001600020819055505b50565b600054600160a060020a031632600160a060020a0316141561017f57610184565b6101c9565b60006001600084600160a060020a031681526020019081526020016000208190555060016001600083600160a060020a03168152602001908152602001600020819055505b5050565b6000600030600160a060020a0316606060020a02815260140187600160a060020a0316606060020a02815260140186600160a060020a0316606060020a028152601401858152602001600020905060016020600060008481526020018760ff168152602001868152602001858152602001600060008560155a03f15050600051600160a060020a0316600054600160a060020a0316141561026d57610272565b61030c565b6002600088600160a060020a0316815260200190815260200160002054851115806102b957506002600087600160a060020a03168152602001908152602001600020548511155b6102c2576102c7565b61030c565b60006001600089600160a060020a031681526020019081526020016000208190555060016001600088600160a060020a03168152602001908152602001600020819055505b50505050505050565b60006001600083600160a060020a03168152602001908152602001600020549050919050565b600054600160a060020a031632600160a060020a0316141561035c57610361565b61036f565b600054600160a060020a0316ff5b56"

abiVoterPool = \
[{"constant" : False,"inputs" : [{"name" : "entry","type" : "address"}],"name" : "add","outputs" : [],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "entry","type" : "address"}],"name" : "remove","outputs" : [],"type" : "function"},{"constant" : True,"inputs" : [{"name" : "entry","type" : "address"}],"name" : "is_voter","outputs" : [{"name" : "ret","type" : "bool"}],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "old","type" : "address"},{"name" : "nu","type" : "address"},{"name" : "editTime","type" : "uint256"},{"name" : "v","type" : "hash8"},{"name" : "r","type" : "hash256"},{"name" : "s","type" : "hash256"}],"name" : "update_for","outputs" : [],"type" : "function"},{"constant" : False,"inputs" : [{"name" : "old","type" : "address"},{"name" : "nu","type" : "address"}],"name" : "update","outputs" : [],"type" : "function"},{"constant" : False,"inputs" : [],"name" : "kill_me","outputs" : [],"type" : "function"}]
