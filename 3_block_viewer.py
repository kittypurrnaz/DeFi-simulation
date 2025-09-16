# block_viewer.py
import os
from web3 import Web3
from dotenv import load_dotenv

def get_block_input():
    """Gets and validates the block number from the user."""
    while True:
        try:
            block_num = int(input("Enter the block number to view: "))
            if block_num < 0:
                print("❌ Block number must be positive.")
                continue
            return block_num
        except ValueError:
            print("❌ Invalid input. Please enter a whole number.")

def main():
    load_dotenv()
    LOCAL_ANVIL_URL = "http://127.0.0.1:8545"

    # --- Connection ---
    w3_local = Web3(Web3.HTTPProvider(LOCAL_ANVIL_URL))
    if not w3_local.is_connected():
        print("❌ Error: Could not connect to Local Anvil Node.")
        return
    print("✅ Connected to Local Anvil Node.")

    block_to_view = get_block_input()

    try:
        print(f"\n🔎 Fetching details for block #{block_to_view}...")
        # Get the block with full transaction objects, not just hashes
        block = w3_local.eth.get_block(block_to_view, full_transactions=True)

        if not block:
            print(f"❌ Block #{block_to_view} not found on the local node.")
            return

        transactions = block['transactions']
        
        print(f"\n{'='*15} Block #{block['number']} {'='*15}")
        print(f"Hash: {block['hash'].hex()}")
        print(f"Parent Hash: {block['parentHash'].hex()}")
        print(f"Timestamp: {block['timestamp']}")
        print(f"Found {len(transactions)} transaction(s).")
        print(f"{'='*40}\n")


        if not transactions:
            print("This block has no transactions.")
        else:
            for i, tx in enumerate(transactions):
                value_in_ether = w3_local.from_wei(tx['value'], 'ether')
                print(f"--- Transaction #{i+1} ---")
                print(f"  Hash:  {tx['hash'].hex()}")
                print(f"  From:  {tx['from']}")
                print(f"  To:    {tx['to']}")
                print(f"  Value: {value_in_ether} ETH\n")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
