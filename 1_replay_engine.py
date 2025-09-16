import os
from web3 import Web3
from dotenv import load_dotenv

# --- Helper Functions ---
def get_user_input():
    """Gets and validates the start block and duration from the user."""
    while True:
        try:
            start_block = int(input("Enter the Start Block number: "))
            duration = int(input("Enter Validation Duration (in blocks): "))
            if start_block < 0 or duration <= 0:
                print("❌ Block numbers must be positive and duration must be greater than 0.")
                continue
            return start_block, duration
        except ValueError:
            print("❌ Invalid input. Please enter whole numbers.")

# --- Main Script ---
def main():
    load_dotenv()
    RPC_URL = os.getenv("RPC_URL")
    LOCAL_ANVIL_URL = "http://127.0.0.1:8545"

    # --- Connections ---
    w3_mainnet = Web3(Web3.HTTPProvider(RPC_URL))
    w3_local = Web3(Web3.HTTPProvider(LOCAL_ANVIL_URL))

    if not w3_mainnet.is_connected() or not w3_local.is_connected():
        print("❌ Error: Could not connect to Mainnet or Local Anvil Node. Please check connections.")
        return

    print("✅ Connected to Mainnet and Local Anvil Node.")
    
    start_block, duration = get_user_input()
    end_block = start_block + duration - 1

    print(f"\n🎯 Target: Validating blocks from {start_block} to {end_block}.")
    
    # --- Score Tracking ---
    total_transactions_validated = 0
    total_perfect_matches = 0

    try:
        # --- Main Validation Loop (iterates through each block) ---
        for block_number in range(start_block, end_block + 1):
            print(f"\n{'='*20} Validating Block #{block_number} {'='*20}")
            
            # --- Fetch Block from both sources ---
            try:
                mainnet_block = w3_mainnet.eth.get_block(block_number, full_transactions=True)
                local_block = w3_local.eth.get_block(block_number, full_transactions=True)
            except Exception as e:
                print(f"❌ Could not fetch block #{block_number}. Does it exist on the fork? Error: {e}")
                continue

            transactions = mainnet_block['transactions']
            print(f"Found {len(transactions)} transactions to validate.")
            
            if not transactions:
                print("No transactions in this block. Skipping.")
                continue

            # --- Inner Loop (iterates through transactions in the block) ---
            for i, mainnet_tx in enumerate(transactions):
                total_transactions_validated += 1
                tx_hash = mainnet_tx['hash']
                
                score = "❌ MISMATCH"

                try:
                    # --- Get receipts from both sources using the transaction hash ---
                    mainnet_receipt = w3_mainnet.eth.get_transaction_receipt(tx_hash)
                    local_receipt = w3_local.eth.get_transaction_receipt(tx_hash)

                    # --- Compare the status of the two receipts ---
                    status_match = local_receipt['status'] == mainnet_receipt['status']
                    
                    if status_match:
                        score = "✅ PERFECT MATCH"
                        total_perfect_matches += 1

                    # --- DETAILED PRINT FORMAT ---
                    print(f"\n--- Transaction #{i+1} ({score}) ---")
                    print(f"  Hash:       0x{mainnet_tx['hash'].hex()}")
                    print(f"  From:       {mainnet_tx['from']}")
                    print(f"  To:         {mainnet_tx['to']}")
                    
                    mainnet_status_str = "Success ✅" if mainnet_receipt['status'] == 1 else "Fail ❌"
                    local_status_str = "Success ✅" if local_receipt['status'] == 1 else "Fail ❌"
                    print(f"  Status:     {mainnet_status_str} (Mainnet) | {local_status_str} (Local)")
                    
                    value_in_ether = w3_mainnet.from_wei(mainnet_tx['value'], 'ether')
                    print(f"  Value:      {value_in_ether} ETH")
                    print(f"  Gas Used:   {mainnet_receipt['gasUsed']:,} (Mainnet) | {local_receipt['gasUsed']:,} (Local)")

                except Exception as e:
                    print(f"\n--- Transaction #{i+1} (❌ ERROR) ---")
                    print(f"  Hash:       0x{mainnet_tx['hash'].hex()}")
                    print(f"  Could not validate transaction. Error: {str(e)[:100]}...")

    except Exception as e:
        print(f"\nAn critical error occurred: {e}")

    # --- FINAL SUMMARY ---
    print(f"\n{'='*20} VALIDATION SUMMARY {'='*20}")
    print(f"Blocks Validated: {start_block} to {end_block} ({duration} block(s))")
    print(f"Total Transactions Validated: {total_transactions_validated}")
    print(f"Perfect Matches: {total_perfect_matches}")

    if total_transactions_validated > 0:
        fidelity_score = (total_perfect_matches / total_transactions_validated) * 100
        print(f"\n🏆 Final Fidelity Score: {fidelity_score:.2f}%")
    else:
        print("\nNo transactions were validated to calculate a score.")

if __name__ == "__main__":
    main()
