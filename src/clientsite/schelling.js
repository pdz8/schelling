var app = angular.module('SchellApp', []);


// Controls the user account panel
app.controller('UserAccount', 
        ['$scope','ethService','schellData',
        function($scope,es,sd) {
    $scope.accs = es.getAccounts();
    $scope.setAccount = function(a) {
        if ($scope.acc != a) { $scope.acc = a; }
        sd.account = a;
        $scope.bal = new BigNumber(es.getBalance(a)).toString(10);
    };
    $scope.setAccount(es.getCoinbase());
}]);


// Allows votes on a contract
app.controller('VotePage', 
        ['$scope','ethService','schellData','util',
        function($scope,es,sd,util) {
    $scope.setContract = function(address) {
        if (!es.isAddress(address)) {
            $scope.c = null;
            return;
        }
        $scope.c = sd.loadContract(address);
    };
    $scope.submitHash = function() {
        var h = sd.account 
                + util.rmox($scope.c.address) 
                + util.rmox(es.fromDecimal($scope.option))
                + util.rmox(es.fromAscii($scope.key));
        h = es.sha3(h);
        $scope.c.ethobj.transact({
            value: web3.fromDecimal($scope.c.downPayment),
            from: sd.account
        }).safe.submit_hash(h);
    };
    $scope.revealHash = function() {
        $scope.c.ethobj.transact({
            from: sd.account
        }).safe.reveal_vote(es.fromDecimal($scope.option),es.fromAscii($scope.key));
    };
    $scope.redeemReward = function() {
        $scope.c.ethobj.transact({
            from: sd.account
        }).safe.redeem();
    };
    $scope.c = null; // This is the contract object

    // Debug only!
    $scope.kill = function() {
        $scope.c.ethobj.transact({
            from: sd.account
        }).safe.kill_me();
    };
}]);


// Create new SchellingCoin contracts
app.controller('CreatePage',
        ['$scope','ethService','schellData','util',
        function($scope,es,sd,util) {
    $scope.startTime = new Date().toLocaleString();
    $scope.hashPeriod = '01:00:00'
    $scope.revealPeriod = '01:00:00'
    $scope.maxOption = 2;
    $scope.downPayment = "1000000000000000000"
    $scope.askQuestion = function() {

    };
}]);


// Provides (wrapped) Ethereum functions
app.factory('ethService', [function() {
    var web3 = require('web3');
    web3.setProvider(new web3.providers.HttpSyncProvider('http://localhost:8080')); // 8080 for cpp/AZ, 8545 for go/mist
    return {
        getAccounts: function() {
            try { return web3.eth.accounts; } catch(e) { return []; }
        },
        getBalance: function(a) {
            try { return web3.eth.balanceAt(a); } catch(e) { return '0x0'; }
        },
        call: function(a) {
            try { return web3.eth.call(a); } catch(e) { return 0; }
        },
        getCoinbase: function() {
            try { return web3.eth.coinbase; } catch(e) { return ''; }
        },
        contract: function(addr,abi) {
            var c = web3.eth.contract(addr,abi);
            c.safe = {}
            abi.map(function(f) {
                c.safe[f.basename] = function() {
                    try { return c[f.basename](arguments); }
                    catch(e) { return 0; }
                }
            });
            return c;
        },
        isAddress: function(a) {
            return a.substring(0,2) == '0x' && a.length == 42 && parseInt(a,16);
        },
        fromAscii: web3.fromAscii,
        fromDecimal: web3.fromDecimal,
        sha3: web3.sha3
    };
}]);


// Allows data to be shared between controllers
// Also interacts with ethereum
app.factory('schellData',
        ['ethService','util','abi',
        function(es,util,abi) {

    var loadContract = function(a) {
        if (!es.isAddress(a)) return null;
        var c = { address: a };
        c.ethobj = es.contract(a,abi.abiTreeBallot)
        c.startTime = util.bigToDate(c.ethobj.call().safe.getStartTime());
        c.revealTime = util.bigToDate(c.ethobj.call().safe.getRevealTime());
        c.redeemTime = util.bigToDate(c.ethobj.call().safe.getRedeemTime());
        c.downPayment = c.ethobj.call().safe.getDownPayment();
        return c;
    }

    return {
        account: "",
        contract: null,
        loadContract: loadContract
    };
}]);



// Obligatory util
app.factory('util', [function() {

    // Convert hex UTC to Date
    var bigToDate = function(b) {
        return b && b.toNumber() ? new Date(b.toNumber() * 1000) : null;
    };

    // Convert hex to integer string
    var hexToBig = function(h) {
        try {
            return new BigNumber(h);
        } catch(e) {
            return new BigNumber(0);
        }
    };

    // Remove 0x that prepends hex number
    var rmox = function(s) {
        if (s.substring(0,2) == "0x") {
            s = s.substring(2,s.length);
        }
        return s;
    };

    // Parse times of form hh:mm:ss to number of seconds
    var parseSeconds = function(t) {
        var num_arr = t.split(':').map(function(s) {
            return Number(s) ? Math.ceil(Math.abs(Number(s))) : 0;
        });
        if (num_arr.length != 3) return 3600;
        return (3600*num_arr[0]) + (60*num_arr[1]) + num_arr[2];
    }

    return {
        bigToDate: bigToDate,
        hexToBig: hexToBig,
        rmox: rmox
    };
}]);




