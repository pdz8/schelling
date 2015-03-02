contract I_Reserve {
  function deregister() {}
  function demand_payment(uint256 amount) {}
}

contract Insurance {

  // Involved parties
  address farm;
  address reserve;
  address authority;

  // Premium payments
  uint256 premium;
  uint256 period;
  uint256 amount_paid;
  uint256 due_date;
  uint256 expiration;

  // Payout
  uint256 reward;
  uint256 threshold; // Pay when below

  // Initialization
  function Insurance(
      address _farm, address _reserve, address _authority,
      uint256 _premium, uint256 _period, uint256 _num_periods,
      uint256 _reward, uint256 _threshold) {
    // Store parameters
    farm = _farm;
    reserve = _reserve;
    authority = _authority;
    premium = _premium;
    period = _period;
    reward = _reward;
    threshold = _threshold;

    // Calculate parameters
    amount_paid = 0;
    due_date = block.timestamp + period;
    expiration = block.timestamp + (period * _num_periods);
  }

  // Trigger reward
  function trigger(uint256 trig_val) {
    if (authority != msg.sender) { return; }
    if (expiration < block.timestamp) { return; }
    if (trig_val < threshold) {
      I_Reserve(reserve).demand_payment(reward);
      I_Reserve(reserve).deregister();
      suicide(farm);
    }
  }

  // Make payment
  function make_payment() {
    amount_paid + msg.value;
    if (amount_paid >= premium) {
      amount_paid -= premium;
      due_date += period;
    }
    if (reserve.balance >= reward) {
      reserve.send(msg.value);
    } else {
      msg.sender.send(msg.value);
    }
  }

  // Enforce payments
  function enforce() {
    if (block.timestamp > expiration || block.timestamp > due_date) {
      I_Reserve(reserve).deregister();
      suicide(reserve);
    }
  }

  // Demo-only
  function kill_me() {
    suicide(msg.sender);
  }
}

