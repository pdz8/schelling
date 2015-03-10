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
        ['$scope','ethService','schellData',
        function($scope,es,sd) {
    $scope.setContract = function(address) {
        $scope.c = sd.loadContract(address);
    };
    $scope.submitHash = function() {

    };
    $scope.revealHash = function() {

    };
    $scope.redeemReward = function() {

    };
}]);


// Provides (wrapped) Ethereum functions
app.factory('ethService', [function() {
    var w = require('web3');
    w.setProvider(new w.providers.HttpSyncProvider('http://localhost:8080')); // 8080 for cpp/AZ, 8545 for go/mist
    return {
        getAccounts: function() {
            try { return w.eth.accounts; } catch(e) { return []; }
        },
        getBalance: function(a) {
            try { return w.eth.balanceAt(a); } catch(e) { return '0x0'; }
        },
        call: function(a) {
            try { return w.eth.call(a); } catch(e) { return null; }
        },
        getCoinbase: function() {
            try { return w.eth.coinbase; } catch(e) { return ''; }
        },
    };
}]);


// Allows data to be shared between controllers
// Also interacts with ethereum
app.factory('schellData',
        ['ethService','util','abi',
        function(es,util,abi) {

    var loadContract = function(a) {
        var c = { address: a };
        if (a.substring(0,2) != '0x') return c;
        try {
            c.startTime = util.hexToDate(es.call({to:a,data:'0xc828371e'}));
            c.revealTime = util.hexToDate(es.call({to:a,data:'0x157b0448'}));
            c.redeemTime = util.hexToDate(es.call({to:a,data:'0xce5ed531'}));
            c.downPayment = new BigNumber(
                es.call({to:a,data:'0xd6dd04f7'})).toString(10);
        } catch(e) {
            // c.question = null;
            // c.startTime = null;
            // c.revealTime = null;
            // c.redeemTime = null;
            // c.downPayment = null;
        }
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
    var hexToDate = function(h) {
        var i = parseInt(h,16);
        return i ? new Date(i * 1000) : null;
    };

    // http://stackoverflow.com/questions/847185/convert-a-unix-timestamp-to-time-in-javascript
    var formatDate = function(datetime) {
        var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        var year = datetime.getFullYear();
        var month = months[datetime.getMonth()];
        var date = datetime.getDate();
        var hour = datetime.getHours();
        var min = datetime.getMinutes();
        var sec = datetime.getSeconds();
        var time = date + ',' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
        return time;
    };

    return {
        formatDate: formatDate,
        hexToDate: hexToDate
    };
}]);




