// Inspired by the Iowa Electronic markets
// http://en.wikipedia.org/wiki/Iowa_Electronic_Markets

// Tokens are generated in pairs and can be sold independently
contract Token {

  // Involved parties
  address owner;
  address awarder;

  // Amount paid to owner if token wins in market
  uint256 option;
  uint256 reward;

  // Selling fields
  uint256 asking_price;
  bool is_for_sale;

  // Create of the token is first to own it
  function Token() {
    owner = msg.sender;
    is_for_sale = false;
  }

  // Put token up for sale by lowering price
  function sell(uint256 _asking_price) {
    is_for_sale = true;
    asking_price = _asking_price;
  }

  // Remove sale posing
  function dont_sell() {
    is_for_sale = false;
  }

  // Attempt to buy the token
  function buy() {
    if (is_for_sale && msg.value >= asking_price) {
      owner.send(msg.value);
      owner = msg.sender;
      is_for_sale = false;
    } else {
      msg.sender.send(msg.value);
    }
  }

  // Initialize token (called by market)
  function set_option(uint256 _option, uint256 _reward) {
    if (tx.origin != owner) return;
    awarder = msg.sender;
    option = _option;
    reward = _reward;
  }

  // Token can be redeemed
  function redeem() {
    Market(awarder).redeem(owner);
  }

  // Only owner can destroy
  function kill_me() {
    if (msg.sender == owner) {
      suicide(owner);
    }
  }

}


// Market which initializes and redeems tokens
// This is a market for binary outcomes
contract Market {

  // Involved parties
  address authority;

  // Registered tokens
  struct OR_PAIR {
    uint256 option;
    uint256 reward;
  }
  mapping (address => OR_PAIR) valid_tokens; // token -> (1 | 2)

  // The awarded option
  uint256 correct_option;

  // Initialize with knowledge of who to get trigger from
  function Market(address _authority) {
    authority = _authority;
  }

  // Initilize two tokens to diffient options
  function buy_bundle(address opt_1, address opt_2) {
    if (valid_tokens[opt_1].option != 0 || valid_tokens[opt_1].option != 0) {
      return;
    }
    valid_tokens[opt_1].option = 1;
    valid_tokens[opt_1].reward = msg.value;
    Token(opt_1).set_option(1, msg.value);
    valid_tokens[opt_2].option = 2;
    valid_tokens[opt_2].reward = msg.value;
    Token(opt_2).set_option(2, msg.value);
  }

  // Set the option
  function trigger(uint256 trig_val) {
    if (authority != msg.sender) return;
    correct_option = trig_val;
  }

  // Redeem token
  function redeem(address payout_addr) {
    if (correct_option == 0) return;
    if (valid_tokens[msg.sender].option == correct_option) {
      valid_tokens[msg.sender].option = 0;
      payout_addr.send(valid_tokens[msg.sender].reward);
    }
    if (address(this).balance == 0) {
      suicide(payout_addr);
    }
  }

  // Demo only
  function kill_me() {
    suicide(msg.sender);
  }

}

