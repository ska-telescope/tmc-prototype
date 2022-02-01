## SdpMasterLeafNode

The primary responsibility of the SDP Master Leaf node is to monitor the SDP Master and issue control
actions during an observation. It also acts as a SDP contact point for Master Node for observation
execution. There is one to one mapping between SDP Master Leaf Node and SDP Master.

## Requirement

- PyTango >= 9.3.3
- devicetest (for using tests)
- sphinx (for building sphinx documentation)

## Installation

Run python setup.py install

If you want to build sphinx documentation,
run python setup.py build_sphinx

If you want to pass the tests, 
run python setup.py test

## Usage

Now you can start your device server in any
Terminal or console by calling it :

SdpMasterLeafNodeDS instance_name
