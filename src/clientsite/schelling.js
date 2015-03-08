var app = angular.module('SchellApp', []);

app.controller('UserAccount', ['$scope','ethService',function($scope,es) {
  $scope.bal = 0;
  $scope.accs = es.accounts;
  $scope.es = es;
  $scope.changeAcc = function() { 
    $scope.bal = es.getBalance($scope.acc)
  };
}]);

app.factory('ethService', [function() {
  var w = require('web3');
  w.setProvider(new w.providers.HttpSyncProvider('http://localhost:8080')); // 8080 for cpp/AZ, 8545 for go/mist
  return {
    accounts: w.eth.accounts,
    getBalance: w.eth.balanceAt
  };
}]);

