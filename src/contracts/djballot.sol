// SchellingCoin implementation designed for CrowdVerity
// Certain aspects of the contract are centralized


// Whitelist pool managed by CrowdVerity
contract VoterPool {

    address owner;
    mapping (address => bool) whiteList;
    mapping (address => uint256) lastEdit;

    function VoterPool() {
        owner = msg.sender;
    }


    //////////////////
    // Transactions //
    //////////////////

    function add(address entry) returns(bool success) {
        if (tx.origin != owner) return false;
        whiteList[entry] = true;
        return true;
    }

    function remove(address entry) returns(bool success) {
        if (tx.origin != owner) return false;
        whiteList[entry] = false;
        return true;
    }

    function update(address old, address nu) returns(bool success) {
        if (tx.origin != owner) return false;
        whiteList[old] = false;
        whiteList[nu] = true;
        return true;
    }

    // Let a non-owner update the pool (with the owner's permission)
    function update_for(
            address old, address nu, uint256 editTime, 
            uint8 v, bytes32 r, bytes32 s) returns(bool success) {

        // Validate request
        bytes32 h = sha3(address(this), old, nu, editTime);
        if (owner != ecrecover(h, v, r, s))
            return false;
        if (editTime <= lastEdit[nu])
            return false;

        // Execute update
        whiteList[old] = false;
        whiteList[nu] = true;
        lastEdit[nu] = editTime;

        // success
        return true;
    }


    ////////////////////////
    // Constant functions //
    ////////////////////////

    // Main interface function
    // Tell if voter is good
    function is_voter(address entry) constant returns(bool ret) {
        return whiteList[entry];
    }

    // Use this as a ping
    function get_owner() constant returns(address ret) {
        return owner;
    }

    // Compute has directly from contract so there is no confusion
    function get_hash(address old, address nu, uint256 editTime)
            constant returns(bytes32 ret) {
        return sha3(address(this), old, nu, editTime);
    }


    //////////////////////////////////////////
    // VoterPool owner may kill at any time //
    //////////////////////////////////////////

    function kill_me() {
        if (tx.origin != owner) return;
        suicide(owner);
    }
}


// Schelling ballot that does not break values into binary representation
// Named DjBallot for Django
contract DjBallot {

    // Authority which chooses voters (parent)
    address pool;
    address asker;

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
    bytes32[8] question;

    // List of address that have submitted hashes
    struct Participant {
        bytes32 h;
        uint256 choice;
        bool redeemed;
        uint256 paid; // Amount of down payment paid for user
    }
    mapping (address => Participant) voterMap;

    // Array of vote revealers
    mapping (uint256 => address) revealers;
    uint256 numRevealed;

    // Vote tallying
    mapping (uint256 => uint256) tally;
    uint256 decision;


    // Constructor
    function DjBallot(
            address _pool, uint256 _maxOption, uint256 _downPayment,
            uint256 _startTime, uint256 _votingPeriod, uint256 _revealPeriod,
            bytes32 _q0, bytes32 _q1, bytes32 _q2, bytes32 _q3,
            bytes32 _q4, bytes32 _q5, bytes32 _q6, bytes32 _q7) {
        pool = _pool;
        maxOption = _maxOption;
        downPayment = _downPayment;
        startTime = _startTime;
        revealTime = startTime + _votingPeriod;
        redeemTime = revealTime + _revealPeriod;
        asker = tx.origin;

        // Get question
        question[0] = _q0;
        question[1] = _q1;
        question[2] = _q2;
        question[3] = _q3;
        question[4] = _q4;
        question[5] = _q5;
        question[6] = _q6;
        question[7] = _q7;
    }


    ////////////////////////
    // Instance functions //
    ////////////////////////

    // Submit hash for myself
    function submit_hash(bytes32 h)
            constant returns(bool success) {

        // Validate input
        if (block.timestamp < startTime || block.timestamp >= revealTime)
            return false;
        address a = tx.origin;
        if (!VoterPool(pool).is_voter(a))
            return false;

        // Update down payment
        voterMap[a].paid += msg.value;

        // Record hash
        voterMap[a].h = h;
        return true;
    }

    // Submit hash of vote for other account
    function submit_hash_for(bytes32 h, uint8 v, bytes32 r, bytes32 s)
            constant returns(bool success) {

        // Assert correct time and voter
        if (block.timestamp < startTime || block.timestamp >= revealTime)
            return false;
        address a = ecrecover(h, v, r, s);
        if (tx.origin != asker && a != tx.origin)
            return false;
        if (!VoterPool(pool).is_voter(a))
            return false;
        
        // Update down payment
        voterMap[a].paid += msg.value;

        // Record hash
        voterMap[a].h = h;
        return true;
    }


    // Default function for receiving payments
    function() {
        if (block.timestamp >= revealTime) return;
        voterMap[tx.origin].paid += msg.value;
    }


    // Reveal hash value and tally the vote
    function reveal_vote_for(address a, uint256 voteVal, bytes32 nonce_hash) 
            constant returns(bool success) {

        // Validate phase and voteVal
        if (block.timestamp < revealTime || block.timestamp >= redeemTime) 
            return false;
        if (voteVal == 0 || voteVal > maxOption)
            return false;

        // Check that deposit has been paid
        if (voterMap[a].paid < downPayment) return false;

        // Check hash
        bytes32 h = sha3(a, address(this), voteVal, nonce_hash);
        if (voterMap[a].h != h) return false;

        // Check if already revealed
        if (voterMap[a].choice == voteVal) return true;

        // Record vote
        voterMap[a].choice = voteVal;
        tally[voteVal]++;

        // Record as revealer
        revealers[numRevealed] = a;
        numRevealed++;
        return true;
    }
    function reveal_hash(uint256 voteVal, bytes32 nonce_hash)
            constant returns(bool success) {
        return this.reveal_vote_for(tx.origin, voteVal, nonce_hash);
    }


    // Tally up votes and redeem winners
    function tally_up() returns(uint256 ret) {

        // Return pre-computed decision
        if (decision != 0) return decision;

        // Check that it is redeem time
        if (block.timestamp < redeemTime) return decision;

        // Calculate the decision
        uint256 i = 1;
        decision = 0;
        while (i <= maxOption) {
            if (tally[i] > tally[decision]) {
                decision = i;
            }
            i++;
        }

        // Give funds to asker if there was no decision
        if (decision == 0) {
            asker.send(address(this).balance);
            return decision;
        }

        // Reward correct revealers
        uint256 reward = address(this).balance / tally[decision];
        i = 0;
        while (i < numRevealed) {
            if (voterMap[revealers[i]].choice == decision) {
                revealers[i].send(reward);
            }
            i++;
        }

        // Output decision
        return decision;
    }


    /////////////
    // Getters //
    /////////////

    // Field getters
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
    function get_num_revealed() constant returns(uint256 ret) {
        return numRevealed;
    }
    function get_question() constant returns(
            bytes32 ret_q0, bytes32 ret_q1, bytes32 ret_q2,
            bytes32 ret_q3, bytes32 ret_q4, bytes32 ret_q5,
            bytes32 ret_q6, bytes32 ret_q7) {
        ret_q0 = question[0];
        ret_q1 = question[1];
        ret_q2 = question[2];
        ret_q3 = question[3];
        ret_q4 = question[4];
        ret_q5 = question[5];
        ret_q6 = question[6];
        ret_q7 = question[7];
    }
    function get_version() constant returns(uint256 ret) {
        return 1;
    }

    // Compute has directly from contract so there is no confusion
    function get_hash(address a, uint256 voteVal, bytes32 nonce_hash)
            constant returns(bytes32 ret) {
        return sha3(a, address(this), voteVal, nonce_hash);
    }


    //////////////////////////////////////////
    // VoterPool owner may kill at any time //
    //////////////////////////////////////////
    
    function kill_me() {
        if (tx.origin == VoterPool(pool).get_owner()) {
            suicide(tx.origin);
        }
    }

}




// vim: set tabstop=4:
// vim: set shiftwidth=4:
// vim: set expandtab:

