// VoterPool in which voter enroll via POW
contract PowList {

  // Challenge nonce to be included in every hash
  hash256 challenge;

  // Scheduling
  uint256 startTime;
  uint256 endTime;

  // Successfull POW enrollees
  mapping (address => bool) whitelisted;

  // Hashes must be below this
  hash256 threshold;

  // Initialize pool with trusted owner
  function PowList(
      uint256 _startTime, uint256 _enrollPeriod,
      hash256 _threshold) {
    startTime = _startTime;
    endTime = startTime + _enrollPeriod;
    threshold = _threshold;
    owner = msg.sender;
  }

  // Set the challenge nonce
  // TODO: make this more unpredictable
  function get_challenge() returns(hash256 ret) {
    if (block.timestamp < startTime) return 0x0;
    if (challenge == 0x0) {
      challenge = sha256(
          address(this).balance,
          block.coinbase,
          block.timestamp,
          block.blockhash(block.number));
    }
    return challenge;
  }

  // Attempt to register to vote
  function enroll(uint256 nonce) {
    if (block.timestamp >= endTime || challenge == 0x0) return;
    hash256 h = sha256(challenge, tx.origin, nonce);
    if (h > threshold) return;
    whitelisted[tx.origin] = true;
  }

  // Is this a voter
  function is_voter(address entry) returns(bool ret) {
    return whitelisted[entry];
  }

  // Pool destruction
  function kill_me() {
    if (block.timestamp < endTime)
    if (msg.sender != owner) return;
    suicide(owner);
  }
  address owner;
}

