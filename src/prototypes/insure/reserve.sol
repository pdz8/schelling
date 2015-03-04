contract Reserve {

  // The insurer which can register new insurance agreements
  address insurer;

  // Registered insurance contracts
  mapping (address => bool) agreements;

  // Constructor (contract init)
  function Reserve() {
    insurer = msg.sender;
    agreements[insurer] = true;
  }

  // Add a registered contract
  function register(address entry) {
    if (msg.sender != insurer) return;
    agreements[entry] = true;
  }

  // Allow contract to deregister itself
  function deregister() {
    agreements[msg.sender] = false;
  }

  // Is this registered
  function is_registered(address entry) returns(bool ret) {
    return agreements[entry];
  }

  // Contract may request payment
  function demand_payment(uint256 amount) {
    if (agreements[msg.sender]) {
      if (address(this).balance >= amount) {
        msg.sender.send(amount);
      } else {
        msg.sender.send(address(this).balance);
      }
    }
  }

  // Demo only feature
  function kill_me() {
    suicide(insurer);
  }
  
}

