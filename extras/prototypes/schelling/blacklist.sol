// Editable list of legal voters
// Meant to serve as an interface that schelling decisions can easily follow
// Implementations can either be whitelists or blacklists
contract BlackList {

  address owner;
  mapping (address => bool) blacklisted;

  // Initialize pool with trusted owner
  function BlackList() {
    owner = msg.sender;
  }

  // Is this a voter
  function is_voter(address entry) returns(bool ret) {
    return !blacklisted[entry];
  }

  // Blacklist the voter
  function ban(address entry) {
    if (msg.sender != owner) return;
    blacklisted[entry] = true;
  }

  // Pool destruction
  function kill_me() {
    if (msg.sender != owner) return;
    suicide(owner);
  }
}

