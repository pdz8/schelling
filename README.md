# CrowdAssert on Ethereum

![Coinye](http://ic.tweakimg.net/ext/i/imagenormal/1393690309.png)
![Nyan](http://www.wired.com/images_blogs/underwire/2014/01/nyan100.gif)

## Setup

#### Installing Ethereum
Instructions for installing cpp-ethereum can be found [here](https://github.com/ethereum/cpp-ethereum/wiki/Installing%20Clients). 
You can then check that everything is installed properly by simply running:

```
eth -h
```

#### Creating an account
By far the friendliest way to setup Ethereum accounts is to use one of the GUI clients.
AlethZero is included with cpp-ethereum and can serve this purpose.

In `ethutils.py` we also provide methods for secret/public key generation.

#### Python
We provide scripts in place of `pyethereum`.  These do not have the all of the same functionality as `pyethereum`, but they are functional.
Install them via:

```
python setup.py install
```

The website for SchellingCoin is served through the Django framework. Version 1.7 is required:

```
pip install Django
```

Sybil attacks are prevent by require every user to register with a Facebook account. This then requires:

```
pip install python-social-auth
```

#### Shell
Common patterns arise when developing and testing the SchellingCoin implementation. We try to collect these patterns into a single helpful script `schellrc.sh`:

```
source schellrc.sh
```


#### Windows
Everything but `pyethereum` works on Windows (TODO: add shocked emoticon). This is a good compromise since `pyethereum` doesn't work well anywhere.


## Schelling contracts

#### Voter pool
Voter pools tell ballot contracts who is 'registered' to vote.
We have a interface established for voter pools so that a ballot need only to call `is_voter(address)` on a pool to tell whether an address represents a registered voter.
The implementation of `is_voter` can vary to include POW, hierarchies, fixed oracles, or no structure at all.

The voter pool we use for CrowdAssert is a simple whitelist. We control who gets let into the pool based on who registers their Facebook account with us.
This is how we prevent Sybil attacks.

#### Ballot
As already mentioned, ballots are the contracts implementing the core SchellingCoin logic.
We currently implement a simple ballot where users choose options between 1 and n. This procedure is as follows:

1. A user proposes creates a ballot, specifying a question, deposit, start time, commit period, and reveal period.
In order to incentivize participation, the creator ought to put some value of Ether into the contract as well.
2. At its start time and until the end of the commit period the ballot opens up to hash submissions.
During this time, registered voters may submit hashes of their votes and deposits to the ballot. Hashes have the form
`
hash256 h = sha3(tx.origin, address(this), voteVal, key);
`
To emulate a commitment scheme, voters are required to hash a key with their votes. We cannot enforce that voters pick good keys or unique keys but we will provide a service for doing this.
3. The reveal phase begins when the commit phase ends. Here voters reveal the votes and keys used to create their hashes.
4. At the end of the reveal phase votes are tallied. Voters that voted for the winning option are awarded a shared of all the deposits from voters and the question asker.

##### Triggers
In order to make ballots useful for other contracts (e.g. insurance or betting) the ballots implement a *trigger* interface.
Such contracts can call `wait_for_decision()` on the ballot contract. This will register the contract as a *waiter* with the ballot.
When the finishes tallying it will then iterate through all the registered waiters and call `trigger(uint256)` with the decided value.


## TODO
This is by no means a complete list. It's just here to prevent memory loss.

* Implement voter tokens for each Facebook user. These replace account addresses in the voter pool and allow voters to rapidly change their voting address.
Currently if a voter changes their registered address multiple times in a commit period, they can submit multiple hashes.
 * Before tokens are implemented, we should enforce some hard-coded rate on address updates in pools. This can be done at the server or in the voter pool contract.
 All ballot contracts would have to keep this hard-coded rate in mind when defining their commit periods. (Maybe we should hard-code the commit period?)
* Enable good support for users to circumvent having to store their secret keys on our server. They could simply register their address to get into the voter pool and then directly interact with the Ethereum blockchain afterwards.
* Check hashes of ballot code and allow ballots to be imported.


