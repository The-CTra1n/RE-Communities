The first thing you need to do is install brownie:
    git clone https://github.com/eth-brownie/brownie.git
    cd brownie
    python3 setup.py install
If this doesn't work, make sure you have python installed. Run:
    python --version
IT should give you something like 3.10
If not, try:
    brew install python
    brew upgrade python3
To get brew, try this (not sure if it works... You may need to follow an online tutorial):
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
The best way to download the latest version is delete your local version of the repo, then run:
    git clone git@github.com:The-CTra1n/RE-Communities.git
You need to set up an ssh key in github to run this.
Follow the instructions here:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
If you want to skip this (it can be a bit messy), just download the repo at
https://github.com/The-CTra1n/RE-Communities/tree/main
Change directory into hello_REC_brownie, then run:
    brownie test tests/test.py -s
This compiles all of your on-chain smart contracts, and runs the code in the tests/test.py file
test.py initializes the system, and iterates through several rounds of encrypted usage uploading and settlement.
