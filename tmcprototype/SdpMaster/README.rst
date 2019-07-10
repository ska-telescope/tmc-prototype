## SdpMaster

The SDP Master implements internal monitor and control functionality for its underlying components
and provides a high-level interface which allows TMC to monitor the status of equipment and processing
resources, and to configure and control the signal processing functions. The interface supports the
following overall functionality:

## Requirement

- PyTango >= 8.1.6
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

SdpMaster instance_name
