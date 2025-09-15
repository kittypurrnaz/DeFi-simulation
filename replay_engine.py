import os
from web3 import Web3
from dotenv import load_dotenv

# --- Helper Functions ---
def get_user_input():
    """Gets and validates the start block and duration from the user."""
    while True:
        try:
            start_block = int(input("Enter the Start Block number: "))
            duration = int(input("Enter Simulation Duration (in blocks): "))
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

    print(f"\n🎯 Target: Replay blocks from {start_block} to {end_block}.")
    print(f"🍴 Make sure Anvil is forked at block: {start_block - 1}\n")

    # --- Score Tracking ---
    total_transactions_processed = 0
    total_perfect_matches = 0

    try:
        # --- Main Simulation Loop (iterates through each block) ---
        for block_number in range(start_block, end_block + 1):
            print(f"\n{'='*20} Processing Block #{block_number} {'='*20}")
            
            original_block = w3_mainnet.eth.get_block(block_number, full_transactions=True)
            transactions = original_block['transactions']
            print(f"Found {len(transactions)} transactions to replay.")
            
            if not transactions:
                print("No transactions in this block. Skipping.")
                continue

            # --- Inner Loop (iterates through transactions in the block) ---
            for i, tx in enumerate(transactions):
                total_transactions_processed += 1
                sender_account = tx['from']
                
                tx_params = {
                    'from': sender_account,
                    'to': tx['to'],
                    'value': tx['value'],
                    'gas': tx['gas'],
                    'maxFeePerGas': tx.get('maxFeePerGas'),
                    'maxPriorityFeePerGas': tx.get('maxPriorityFeePerGas'),
                    'nonce': tx['nonce'],
                    'data': tx['input'],
                    'chainId': w3_local.eth.chain_id
                }

                if tx_params['maxFeePerGas'] is None:
                    tx_params.pop('maxFeePerGas')
                    tx_params.pop('maxPriorityFeePerGas')
                    tx_params['gasPrice'] = tx.get('gasPrice')
                
                w3_local.provider.make_request("anvil_impersonateAccount", [sender_account])
                
                score = "❌ FAILED TO REPLAY"
                
                try:
                    local_tx_hash = w3_local.eth.send_transaction(tx_params)
                    local_receipt = w3_local.eth.wait_for_transaction_receipt(local_tx_hash)
                    original_receipt = w3_mainnet.eth.get_transaction_receipt(tx['hash'])
                    
                    gas_used_match = local_receipt['gasUsed'] == original_receipt['gasUsed']
                    status_match = local_receipt['status'] == original_receipt['status']
                    
                    if gas_used_match and status_match:
                        score = "✅ PERFECT MATCH"
                        total_perfect_matches += 1
                    else:
                        score = "❌ MISMATCH"

                    # --- DETAILED PRINT FORMAT ---
                    print(f"\n--- Transaction #{i+1} ({score}) ---")
                    print(f"  Hash:      0x{tx['hash'].hex()}")
                    print(f"  From:      {tx['from']}")
                    print(f"  To:        {tx['to']}")
                    
                    # NEW: Print the status
                    mainnet_status = "Success" if original_receipt['status'] == 1 else "Fail"
                    local_status = "Success" if local_receipt['status'] == 1 else "Fail"
                    print(f"  Status:    {mainnet_status} (Mainnet) | {local_status} (Local)")

                    print(f"  Gas Used:  {original_receipt['gasUsed']:,} (Mainnet) | {local_receipt['gasUsed']:,} (Local)")
                    gas_price_gwei = w3_mainnet.from_wei(tx.get('gasPrice', 0), 'gwei')
                    print(f"  Gas Price: {gas_price_gwei:.2f} Gwei")


                except Exception as e:
                    original_receipt = w3_mainnet.eth.get_transaction_receipt(tx['hash'])
                    print(f"\n--- Transaction #{i+1} ({score}) ---")
                    print(f"  Hash:      0x{tx['hash'].hex()}")
                    print(f"  From:      {tx['from']}")
                    print(f"  To:        {tx['to']}")
                    print(f"  Error:     {str(e)[:100]}...")

                w3_local.provider.make_request("anvil_stopImpersonatingAccount", [sender_account])

    except Exception as e:
        print(f"\nAn critical error occurred: {e}")

    # --- FINAL SUMMARY ---
    print(f"\n{'='*20} SIMULATION SUMMARY {'='*20}")
    print(f"Blocks Processed: {start_block} to {end_block} ({duration} block(s))")
    print(f"Total Transactions Processed: {total_transactions_processed}")
    print(f"Perfect Matches: {total_perfect_matches}")

    if total_transactions_processed > 0:
        fidelity_score = (total_perfect_matches / total_transactions_processed) * 100
        print(f"\n🏆 Final Fidelity Score: {fidelity_score:.2f}%")
    else:
        print("\nNo transactions were processed to calculate a score.")

if __name__ == "__main__":
    main()
