// Schelling Coin implementation with a hierarchy of voter pools
// Each ballot creates a pool for the correct voters and incorrect voters
// A future ballot-maker can choose whichever pool they trust more


// Node in the tree of voter pools
// Acts as a simple whitelist
contract TreePool {

  address owner;
  mapping (address => bool) whitelist;

  // Establish ballot as creator
  function TreePool() {
    owner = msg.sender;
  }

  // Creator ballot may register voters into pool
  function register(address entry) {
    if (msg.sender == owner) {
      whitelist[entry] = true;
    }
  }

  // Check the whitelist
  function is_voter(address entry) returns(bool ret) {
    return whitelist[entry];
  }

  // Demo only
  function kill_me() {
    suicide(msg.sender);
  }
}


// Schelling ballot that does not break values into binary representation
contract TreeBallot {

  // Authority which chooses voters (parent)
  address pool;

  // Child voter pools
  address rightPool;
  address wrongPool;

  // Choice range (0 is not at option)
  uint256 maxOption;

  // Voting down payment
  uint256 downPayment;
  uint256 reward;

  // Ballot schedule
  uint256 startTime;
  uint256 revealTime;
  uint256 redeemTime;

  // TODO
  // When array support comes out allow the question string to be stored

  // List of address that have submitted hashes
  struct Participant {
    hash256 h;
    uint256 choice;
    bool redeemed;
  }
  mapping (address => Participant) voterMap;

  // Vote tallying
  mapping (uint256 => uint256) tally;
  uint256 decision;


  // Constructor
  function TreeBallot(
      address _pool, uint256 _maxOption, uint256 _downPayment,
      uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod) {
    pool = _pool;
    maxOption = _maxOption;
    downPayment = _downPayment;
    startTime = _startTime;
    revealTime = startTime + _votingPeriod;
    redeemTime = revealTime + _revealPeriod;
  }


  // Submit hash of vote
  function submit_hash(hash256 h) {
    if (block.timestamp < startTime || block.timestamp >= revealTime) return;
    if (voterMap[tx.origin].h != 0x0) return;
    if (!TreePool(pool).is_voter(tx.origin)) return;
    if (msg.value < downPayment) return;
    voterMap[tx.origin].h = h;
  }


  // Reveal hash value and tally the vote
  function reveal_vote(uint256 voteVal, uint256 key) {

    // Validate input
    if (block.timestamp < revealTime || block.timestamp >= redeemTime) return;
    if (voteVal == 0 || voteVal > maxOption) return;
    // if (voterMap[tx.origin].h == 0x0) return;

    // Check hash and vote if good
    hash256 h = sha256(tx.origin, address(this), voteVal, key);
    if (voterMap[tx.origin].h == h) {
      voterMap[tx.origin].choice = voteVal;
      tally[voteVal]++;
    }
  }


  // Get rewarded for vote
  function redeem() {

    // Validate input
    if (block.timestamp < redeemTime) return;

    // Choose winner if necessary
    if (decision == 0) {
      uint256 i = 1;
      decision = 0;
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
    if (voterMap[tx.origin].choice == decision 
        && !voterMap[tx.origin].redeemed) {
      voterMap[tx.origin].redeemed = true;
      tx.origin.send(reward);
    }
  }


  // Request to be put in a forked pool
  function fork() {
    if (voterMap[tx.origin].choice == 0) return;
    if (voterMap[tx.origin].choice == decision) {
      if (rightPool == 0x0) {
        rightPool = address(new TreePool());
      }
      TreePool(rightPool).register(tx.origin);
    } else {
      if (wrongPool == 0x0) {
        wrongPool = address(new TreePool());
      }
      TreePool(wrongPool).register(tx.origin);
    }
  }


  // Debug only
  function kill_me() {
    suicide(tx.origin);
  }

}




// vim: set tabstop=2:
// vim: set shiftwidth=2:

