// SchellingCoin implementation designed for Schango site
// Certain aspects of the contract are centralized


// Whitelist pool managed by Schango
contract VoterPool {

    address owner;
    mapping (address => bool) whiteList;
    mapping (address => uint256) lastEdit;

    function VoterPool() {
        owner = msg.sender;
    }

    function add(address entry) {
        if (tx.origin != owner) return;
        whiteList[entry] = true;
    }

    function remove(address entry) {
        if (tx.origin != owner) return;
        whiteList[entry] = false;
    }

    function update(address old, address nu) {
        if (tx.origin != owner) return;
        whiteList[old] = false;
        whiteList[nu] = true;
    }

    // Let a non-owner update the pool (with the owner's permission)
    function update_for(
            address old, address nu, uint256 editTime, 
            hash8 v, hash256 r, hash256 s) {
        // Validate request
        hash256 h = sha3(address(this), old, nu, editTime);
        if (owner != ecrecover(h, v, r, s)) return;
        if (editTime <= lastEdit[old] || editTime <= lastEdit[nu]) return;

        // Execute update
        whiteList[old] = false;
        whiteList[nu] = true;
    }

    function is_voter(address entry) constant returns(bool ret) {
        return whiteList[entry];
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
    string32[5] question;

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
            uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod,
            string32 _q0, string32 _q1, string32 _q2,
            string32 _q3, string32 _q4) {
        pool = _pool;
        maxOption = _maxOption;
        downPayment = _downPayment;
        startTime = _startTime;
        revealTime = startTime + _votingPeriod;
        redeemTime = revealTime + _revealPeriod;
        owner = msg.sender;

        // Get question
        question[0] = _q0;
        question[1] = _q1;
        question[2] = _q2;
        question[3] = _q3;
        question[4] = _q4;
    }

    // Signature of constructor hack
    function constructor_sig(
            address _pool, uint256 _maxOption, uint256 _downPayment,
            uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod,
            string32 _q0, string32 _q1, string32 _q2,
            string32 _q3, string32 _q4) {}


    // Register a trigger for another contract
    function wait_for_decision() {
        waiters[numWaiting] = msg.sender;
        numWaiting++;
    }

    // Get hash directly from contract so there is no confusion
    function get_hash(address a, uint256 voteVal, hash256 nonce_hash) constant returns(hash256 ret) {
        return sha3(a, address(this), voteVal, nonce_hash);
    }

    // Submit hash for myself
    function submit_hash(hash256 h) {

        // Validate input
        if (block.timestamp < startTime || block.timestamp >= revealTime) return;
        address a = tx.origin;
        if (!VoterPool(pool).is_voter(a)) return;

        // Update down payment
        voterMap[a].paid += msg.value;

        // Record hash
        voterMap[a].h = h;
    }

    // Submit hash of vote for other account
    function submit_hash_for(hash256 h, hash8 v, hash256 r, hash256 s) {

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
    function reveal_vote_for(address a, uint256 voteVal, hash256 nonce_hash) {

        // Validate input
        if (block.timestamp < revealTime || block.timestamp >= redeemTime) return;
        if (voteVal == 0 || voteVal > maxOption) return;

        // Check hash and vote if good
        hash256 h = sha3(a, address(this), voteVal, nonce_hash);
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
    function reveal_hash(uint256 voteVal, hash256 nonce_hash) {
        this.reveal_vote_for(tx.origin, voteVal, nonce_hash);
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
    function get_max_option() constant returns(uint256 ret) {
        return maxOption;
    }
    function get_start_time() constant returns(uint256 ret) {
        return startTime;
    }
    function get_reveal_time() constant returns(uint256 ret) {
        return revealTime;
    }
    function get_redeem_time() constant returns(uint256 ret) {
        return redeemTime;
    }
    function get_down_payment() constant returns(uint256 ret) {
        return downPayment;
    }
    function get_decision() constant returns(uint256 ret) {
        return decision;
    }
    function get_question() constant returns(
            string32 ret_q0, string32 ret_q1, string32 ret_q2,
            string32 ret_q3, string32 ret_q4) {
        ret_q0 = question[0];
        ret_q1 = question[1];
        ret_q2 = question[2];
        ret_q3 = question[3];
        ret_q4 = question[4];
    }


    // Debug only
    function kill_me() {
        suicide(tx.origin);
    }

}




// vim: set tabstop=4:
// vim: set shiftwidth=4:
// vim: set expandtab:

