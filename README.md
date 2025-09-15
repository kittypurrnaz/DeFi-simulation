# Blockchain Transaction Verifier

This script replays transactions from a specific Ethereum mainnet block on a local Anvil fork to verify that the outcomes are identical.

## Setup
1. Clone this repository.
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add your `RPC_URL`.

## How to Run
1. Start Anvil in one terminal: `anvil --fork-url <Your-RPC-URL> --fork-block-number <Block-1>`
2. Run the script in another terminal: `python3 verification.py`
