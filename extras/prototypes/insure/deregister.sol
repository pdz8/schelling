contract I_Reserve {
  function deregister() {}
  function demand_payment(uint256 amount) {}
}

contract Optout {

  function test_demand(address a) {
    I_Reserve(a).demand_payment(1 ether);
  }

  function test_dereg(address a) {
    I_Reserve(a).deregister();
  }

  function test_mulcall(address a) {
    I_Reserve(a).demand_payment(1 ether);
    I_Reserve(a).deregister();
  }

  function kill_me() {
    suicide(msg.sender);
  }
}
