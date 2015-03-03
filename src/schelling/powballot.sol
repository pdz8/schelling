// Schelling Coin implementation

// Schelling ballot that does not break values into binary representation
contract OptionBallot {


  // Authority which chooses voters
  address authorities;

  // Choice range (0 is not at option)
  uint256 maxOption;

  // Voting down payment
  uint256 downPayment;
  uint256 reward;

  // Ballot schedule
  uint256 startTime;
  uint256 revealTime;
  uint256 redeemTime;

  // POW fields
  hash256 threshold;
  hash256 challenge;

  // TODO
  // When array support comes out allow the question string to be stored

  // List of address that have submitted hashes
  struct Participant {
    bool enrolled;
    hash256 h;
    uint256 choice;
    bool redeemed;
  }
  mapping (address => Participant) voterMap;

  // Vote tallying
  mapping (uint256 => uint256) tally;
  uint256 numTallied;
  uint256 decision;
  uint256 numRedeemed;


  // Constructor
  function OptionBallot(
      address _authorities, uint256 _maxOption, uint256 _downPayment,
      uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod,
      hash256 _threshold) {
    authorities = _authorities;
    maxOption = _maxOption;
    downPayment = _downPayment;
    startTime = _startTime;
    revealTime = startTime + _votingPeriod;
    redeemTime = revealTime + _revealPeriod;
    threshold = _threshold;
  }


  // Pay downpayment to enroll
  function enroll() {
    if (block.timestamp >= startTime || msg.value < downPayment) {
      // tx.origin.send(msg.value);
    } else {
      voterMap[tx.origin].enrolled = true; 
    }
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


  // Submit hash of vote
  function submit_hash(hash256 h) {
    if (block.timestamp < startTime || block.timestamp >= revealTime) return;
    if (!voterMap[tx.origin].enrolled) return;
    if (challenge == 0x0) return;
    if (h > threshold) return;
    if (!I_VoterPool(authorities).is_voter(tx.origin)) return; // May not be needed
    voterMap[tx.origin].h = h;
  }


  // Reveal hash value and tally the vote
  function reveal_vote(uint256 voteVal, uint256 key, uint256 nonce) {

    // Validate input
    if (block.timestamp < revealTime || block.timestamp >= redeemTime) return;
    if (voteVal == 0 || voteVal > maxOption) return;
    // if (voterMap[tx.origin].h == 0x0) return;

    // Check hash and vote if good
    hash256 h = sha256(tx.origin, address(this), voteVal, key, nonce);
    if (voterMap[tx.origin].h != h) return;
    voterMap[tx.origin].choice = voteVal;
    tally[voteVal]++;
    numTallied++;
  }


  // Get rewarded for vote
  function redeem() {

    // Validate input
    if (block.timestamp < redeemTime) return;

    // Choose winner if necessary
    if (decision == 0) {
      uint256 i = 2;
      decision = 1;
      while (i <= maxOption) {
        if (tally[i] > tally[decision]) {
          decision = i;
        }
        i++;
      }
      if (decision == 0) return;
      reward = address(this).balance / tally[decision];
    }

    // Reward voter
    if (voterMap[tx.origin].choice == decision) {
      voterMap[tx.origin].h = 0;
      voterMap[tx.origin].choice == 0;
      tx.origin.send(reward);
      numRedeemed++;
      if (numRedeemed == numTallied) {
        suicide(authorities);
      }
    }
  }


  // Debug only
  function kill_me() {
    suicide(tx.origin);
  }

}


// Voter pool interface
contract I_VoterPool {
  function is_voter(address entry) returns(bool ret) {
    return true;
  }
  function kill_me() {
    suicide(msg.sender);
  }
}



// vim: set tabstop=2:
// vim: set shiftwidth=2:

