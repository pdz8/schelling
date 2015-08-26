# CrowdVerity on Ethereum

![Coinye](http://ic.tweakimg.net/ext/i/imagenormal/1393690309.png)
![Nyan](http://www.wired.com/images_blogs/underwire/2014/01/nyan100.gif)

## Setup

#### Python dependencies

The provided `pyschelling` package requires the following packages:

```
pip install docopt
pip install bitcoin
pip install requests
pip install pysha3
pip install pybitcointools
```

The website for SchellingCoin is served through the Django framework. Version 1.7 is required:

```
pip install Django
```

We using Facebook authentication as a Sybil attack countermeasure. This requires:

```
pip install python-social-auth
```

#### pyethapp

The Ethereum client used by the CrowdVerity server is a modified version of `pyethapp` found [here](https://github.com/pdz8/pyethapp).
Setup is as follows:

```
git clone https://github.com/pdz8/pyethapp.git
cd pyethapp
python setup.py install
```

Additional help can be found in the documentation for the [original](https://github.com/ethereum/pyethapp) `pyethapp` app.


## Running CrowdVerity

#### pyethapp

Not surprisingly, the custom Ethereum client must run in the background in order to interact with Ethereum.
Run `pyethapp` with no arguments to view usage.
Also refer to the [official documentation](https://github.com/ethereum/pyethapp) for the most up to date guides.

#### Django
The actually CrowdVerity site behaves like any other Django site:

```
python manage.py runserver 0.0.0.0:8000
```

Also remember to properly load static files following every update to them:

```
python manage.py collectstatic
```

Settings are split between the typical `settings.py` and a `local_settings.py` which is purposely ignored from this repository.
`local_settings.py` overrides `settings.py` with secret parameters not meant to be shared in the open git repository.


<!-- The file `/etc/init/ethnode.conf` contains the upstart configuration. Make sure that the node is set to only accept connections from the webserver: -->


## Developing
#### Shell
Common patterns arise when developing and testing the SchellingCoin implementation.
We try to collect these patterns into a single helpful script `schellrc.sh`.
Its source contains a number of useful variables, aliases, and functions for development.

#### Creating an account
A very common task during test loop is to create Ethereum accounts. This task is handled within `ethutils.py` (among many other things) so that the full blown Ethereum clients don't have to be run:

```python
from ethutils import *
secret_key = keccak('blahhhhhh')
eth_address = priv_to_addr(secret_key)
```

#### Interacting with Ethereum
The `ethrpc.py` package provides many tools for interacting with Ethereum contracts and account. A subset of these are available directly from the command-line (`./ethrpc.py -h`).


#### Compiling Solidity
The Python script `solctopy.py` within `<repo root>/src/contracts/` is used to compile Solidity scripts into a form compatible with the Django site.
Execute the following from `<repo root>/src/contracts/` to update the compiled contracts of CrowdVerity:

```
./solctopy.py djballot.sol ../schango/pyschelling/contractbin.py
```

`solctopy.py` uses the `solc` compiler from the cpp-ethereum version of Ethereum.
Instructions for installing cpp-ethereum can be found [here](https://github.com/ethereum/cpp-ethereum/wiki/Installing%20Clients).


## Schelling contracts

#### Voter pool
Voter pools tell ballot contracts who is 'registered' to vote.
We have a interface established for voter pools so that a ballot need only to call `is_voter(address)` on a pool to tell whether an address represents a registered voter.
The implementation of `is_voter` can vary to include POW, hierarchies, fixed oracles, or no structure at all.

The voter pool we use for CrowdVerity is a simple whitelist. We control who gets let into the pool based on who registers their Facebook account with us.
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


