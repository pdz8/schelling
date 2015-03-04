# SchellingCoin on Ethereum

## Setup

#### Installing Ethereum
Instructions for installing cpp-ethereum can be found [here](https://github.com/ethereum/cpp-ethereum/wiki/Installing%20Clients). 
You can then check that everything is installed properly by simply running:

```
eth -h
```

The provided link above also gives instructions for building from source. This is also advisable since Ethereum is still under development. Many weird bugs seem to disappear.

The installation gives an assortment of clients and tools. So far we focus mostly on AlethZero (GUI) and `eth` (CLI).
In the future we will ramp up in Mix, an IDE for Ethereum. It should alleviate many testing inconveniences.

#### Creating an account
The Ethereum clients currently generate a default account upon first use.
For testing purposes however it is useful to generate more accounts.

By far the friendliest way to setup Ethereum accounts is to use one of the GUI clients.
AlethZero is included with cpp-ethereum and can serve this purpose.

It currently seems like the CLI `eth` is unable to generate accounts past its coinbase.
Thus in order to use it, you must first export keys from AlethZero and pass them as arguments to `eth`.
Additionally each instance of `eth` only supports a single account at a time. Thus to run a multi-account scenario one must either use AlethZero or run multiple instances of `eth`, each listening on a different port.

#### Python
The SchelllingCoin implementation is currently a pile of scripts and needs no compilation/installation.
In order to run the scripts it may be necessary to install some additional packages via `pip`, but this should not be trouble. We will include a `setup.py` for this purpose at some point.

#### Windows
Everything but `pyethereum` works on Windows (TODO: add shocked emoticon). This is a good compromise since `pyethereum` doesn't work well anywhere.


## Ballot types

We currently have multiple proposed protocols for SchellingCoin. A brief overview of them is given here. More can be seen in the contracts themselves.

#### Option ballot
This is the standard SchellingCoin ballot which lets voters choose one of a set number of options (encoded as a number between 1 and n).
The procedure is as follows:

1. Voters enroll into the voting pool of the ballot contract. The voting pools may have their own procedures necessary for enrollment. This may include proof-of-work, E-mail verification, etc. After enrollment voters wait for the ballot's start time.
2. At its start time, the ballot allows enrolled voters to submit hashes of their vote along with down payments asserting the correctness of the vote. Hashes have the form
```
hash256 h = sha256(tx.origin, address(this), voteVal, key);
```
To emulate a commitment scheme, voters are required to hash a key with their votes. We cannot enforce that voters pick good keys or unique keys.
3. The hash submission phase ends after a set amount of time and leads into the reveal phase. Here voters reveal the votes and keys used to create their hashes. If the hash checks out the vote is tallied.
4. Finally, once the reveal phase is over, the contract enters the redeem phase. This lets voters who were in the majority redeem their winnings.


#### POW ballot
A proof-of-work ballot is the same as a regular ballot except hashes must now be lower than some threshold.
Thus a double-voter needs to have lots of computational power to submit all his votes.
To further discourage cheating the down payment by the voters is moved to a enroll phase that occurs before hash submission. In order to cheat with many voters, you would have to put up a large sum in the beginning without a guarantee that all of your votes would be recorded.

It's worth noting here that the length of the hash submission phase and size of the POW threshold can be varied. Ideally they should be configured so that an average CPU would take most of the phase's period to submit a valid hash.

#### Tree ballot
The tree ballot is another close variation of the regular SchellingCoin ballot.
The only difference here is that the ballot has the ability to spawn two new voting pool branches after its election is done. One pool is for majority voters and the other for minority voters.

The hope for the tree ballot is that it creates more and more trustworthy voter pools each generation.
Ballot-makers want to have honest pools voting on their questions. Thus they will pick the correct branch to base their ballot upon.


