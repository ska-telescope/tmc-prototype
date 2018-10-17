# tmc-prototype
##About
This is the repository for TMC evolutionary prototype. The goal of this repository is to create evolutionary prototype for Telescope Monitoring and Control package SKA Telescope Manager.

##Install
TBD

##Testing
* **Always** use a virtual environment like `virtualenv` or `anaconda`
* Put tests into the `tests` folder
* Use [PyTest](https://pytest.org) as the testing framework
  - Reference: [PyTest introduction](http://pythontesting.net/framework/pytest/pytest-introduction/)
* Run tests with `python setup.py test`
  - Configure PyTest in `setup.py` and `setup.cfg`
* Running the test creates the `htmlcov` folder
    - Inside this folder a rundown of the issues found will be accessible using the `index.html` file
* All the tests should pass before merging the code 
