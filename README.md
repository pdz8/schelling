# SchellingCoin on Ethereum

## Setup

### Installing Ethereum
Instructions for installing cpp-ethereum can be found [here](https://github.com/ethereum/cpp-ethereum/wiki/Installing%20Clients). 
You can then check that everything is installed properly by simply running:

```
eth -h
```

The provided link above also gives instructions for building from source. This is also advisable since Ethereum is still under development. Many weird bugs seem to disappear.

The installation gives an assortment of clients and tools. So far we focus mostly on AlethZero (GUI) and `eth` (CLI).
In the future we will ramp up in Mix, an IDE for Ethereum. It should alleviate many testing inconveniences.

### Creating an account
The Ethereum clients currently generate a default account upon first use.
For testing purposes however it is useful to generate more accounts.

By far the friendliest way to setup Ethereum accounts is to use one of the GUI clients.
AlethZero is included with cpp-ethereum and can serve this purpose.

It currently seems like the CLI `eth` is unable to generate accounts past its coinbase.
Thus in order to use it, you must first export keys from AlethZero and pass them as arguments to `eth`.
Additionally each instance of `eth` only supports a single account at a time. Thus to run a multi-account scenario one must either use AlethZero or run multiple instances of `eth`, each listening on a different port.

### Python
The SchelllingCoin implementation is currently a pile of scripts and needs no compilation/installation.
In order to run the scripts it may be necessary to install some additional packages via `pip`, but this should not be trouble. We will include a `setup.py` for this purpose at some point.

### Windows
Everything but `pyethereum` works on Windows (TODO: add shocked emoticon). This is a good compromise since `pyethereum` doesn't work well anywhere.
