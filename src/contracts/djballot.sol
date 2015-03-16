// SchellingCoin implementation designed for Schango site
// Certain aspects of the contract are centralized


// Whitelist pool managed by Schango
contract VoterPool {

    address owner;
    mapping (address => bool) whitelist;

    function VoterPool() {
        owner = msg.sender;
    }

    function add(address entry) {
        if (tx.origin != owner) return;
        whitelist[entry] = true;
    }

    function remove(address entry) {
        if (tx.origin != owner) return;
        whitelist[entry] = false;
    }

    function update(address old, address nu) {
        if (tx.origin != owner) return;
        whitelist[old] = false;
        whitelist[nu] = true;
    }

    function is_voter(address entry) constant returns(bool ret) {
        return true;
    }

    function kill_me() {
        if (tx.origin != owner) return;
        suicide(owner);
    }
}


// Interface of contract waiting to be triggered
contract IWait {
    function trigger(uint256 tval) {
        return;
    }
}


// Schelling ballot that does not break values into binary representation
// Named DjBallot for Django
contract DjBallot {

    // Authority which chooses voters (parent)
    address pool;
    address owner;

    // Choice range (0 is not at option)
    uint256 maxOption;

    // Voting down payment
    uint256 downPayment;

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
        uint256 paid; // Amount of down payment paid for user
    }
    mapping (address => Participant) voterMap;

    // Array of vote revealers
    mapping (uint256 => address) revealers;
    uint256 numRevealed;

    // Array of contracts to trigger
    mapping (uint256 => address) waiters;
    uint256 numWaiting;

    // Vote tallying
    mapping (uint256 => uint256) tally;
    uint256 decision;


    // Constructor
    function DjBallot(
            address _pool, uint256 _maxOption, uint256 _downPayment,
            uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod) {
        pool = _pool;
        maxOption = _maxOption;
        downPayment = _downPayment;
        startTime = _startTime;
        revealTime = startTime + _votingPeriod;
        redeemTime = revealTime + _revealPeriod;
        owner = msg.sender;
    }

    // Signature of constructor hack
    function constructor_sig(
            address _pool, uint256 _maxOption, uint256 _downPayment,
            uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod) {}


    // Register a trigger for another contract
    function wait_for_decision() {
        waiters[numWaiting] = msg.sender;
        numWaiting++;
    }


    // Submit hash of vote
    function submit_hash(hash256 h, hash8 v, hash256 r, hash256 s) {

        // Assert correct time and voter
        if (block.timestamp < startTime || block.timestamp >= revealTime) return;
        address a = ecrecover(h, v, r, s);
        if (tx.origin != owner && a != tx.origin) return;
        if (!VoterPool(pool).is_voter(a)) return;
        
        // Update down payment
        voterMap[a].paid += msg.value;

        // Record hash
        voterMap[a].h = h;
    }


    // Default function for receiving payments
    function() {
        if (block.timestamp >= revealTime) return;
        voterMap[tx.origin].paid += msg.value;
    }


    // Reveal hash value and tally the vote
    function reveal_vote_for(address a, uint256 voteVal, uint256 key) {

        // Validate input
        if (block.timestamp < revealTime || block.timestamp >= redeemTime) return;
        if (voteVal == 0 || voteVal > maxOption) return;

        // Check hash and vote if good
        hash256 h = sha3(a, address(this), voteVal, key);
        if (voterMap[tx.origin].h == h)
        {
            // Record vote
            voterMap[tx.origin].choice = voteVal;
            tally[voteVal]++;

            // Record as revealer
            revealers[numRevealed] = a;
            numRevealed++;
        }
    }


    // Tally up votes and redeem winners
    function tally_up() {

        // Validate input
        if (block.timestamp < redeemTime) return;
        if (decision != 0) return;

        // Calculate decision and reward
        uint256 i = 1;
        decision = 0;
        while (i <= maxOption) {
            if (tally[i] > tally[decision]) {
                decision = i;
            }
            i++;
        }
        if (decision == 0) return;
        uint256 reward = address(this).balance / tally[decision];

        // Reward correct revealers
        i = 0;
        while (i < numRevealed) {
            if (voterMap[revealers[i]].choice == decision) {
                revealers[i].send(reward);
            }
        }

        // Notify waiters
        i = 0;
        while (i < numWaiting) {
            IWait(waiters[i]).trigger(decision);
        }
    }

    
    // Getters
    function getMaxOption() constant returns(uint256 ret) {
        return maxOption;
    }
    function getStartTime() constant returns(uint256 ret) {
        return startTime;
    }
    function getRevealTime() constant returns(uint256 ret) {
        return revealTime;
    }
    function getRedeemTime() constant returns(uint256 ret) {
        return redeemTime;
    }
    function getDownPayment() constant returns(uint256 ret) {
        return downPayment;
    }
    function getDecision() constant returns(uint256 ret) {
        return decision;
    }


    // Debug only
    function kill_me() {
        suicide(tx.origin);
    }

}




// vim: set tabstop=4:
// vim: set shiftwidth=4:
// vim: set expandtab:

