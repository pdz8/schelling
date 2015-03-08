var app = angular.module('SchellApp', []);


// Controls the user account panel
app.controller('UserAccount', 
        ['$scope','ethService','shareData',
        function($scope,es,sd) {
    $scope.accs = es.accounts;
    $scope.setAccount = function(a) {
        if ($scope.acc != a) { $scope.acc = a; }
        sd.account = a;
        $scope.bal = new BigNumber(es.getBalance(a)).toString(10);
    };
    $scope.setAccount(es.coinbase);
}]);


// Provides (wrapped) Ethereum functions
app.factory('ethService', [function() {
    // var bn = require('BigNumber');
    var w = require('web3');
    w.setProvider(new w.providers.HttpSyncProvider('http://localhost:8080')); // 8080 for cpp/AZ, 8545 for go/mist
    return {
        // bn: bn,
        accounts: w.eth.accounts,
        getBalance: w.eth.balanceAt,
        coinbase: w.eth.coinbase
    };
}]);


// Allows data to be shared between controllers
app.factory('shareData', [function() {
    return {
        account: "",
        contract: ""
    };
}]);




