# injector_at_fork.py
import os
from web3 import Web3
from dotenv import load_dotenv

def main():
    load_dotenv()
    LOCAL_ANVIL_URL = "http://127.0.0.1:8545"

    # --- Connection ---
    w3_local = Web3(Web3.HTTPProvider(LOCAL_ANVIL_URL))
    if not w3_local.is_connected():
        print("❌ Error: Could not connect to Local Anvil Node.")
        return
    
    fork_block_number = w3_local.eth.block_number
    print(f"✅ Connected to Anvil. Forked at block #{fork_block_number}.")

    # --- Anvil Dummy Account Details ---
    sender_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    sender_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    receiver_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" # Anvil Account #1

    # --- Craft the Transaction ---
    print("\nCrafting transaction to be injected...")
    nonce = w3_local.eth.get_transaction_count(sender_address)
    
    tx_params = {
        'from': sender_address,
        'to': receiver_address,
        'value': w3_local.to_wei(0.5, 'ether'), # Send 0.5 ETH
        'gas': 21000,
        'gasPrice': w3_local.to_wei('10', 'gwei'),
        'nonce': nonce,
        'chainId': w3_local.eth.chain_id
    }

    # --- Sign and Send ---
    try:
        print("Signing and sending...")
        signed_tx = w3_local.eth.account.sign_transaction(tx_params, sender_private_key)
        tx_hash = w3_local.eth.send_raw_transaction(signed_tx.raw_transaction)

        print("Waiting for transaction receipt...")
        tx_receipt = w3_local.eth.wait_for_transaction_receipt(tx_hash)

        new_block_number = tx_receipt['blockNumber']
        print("\n🎉 Success! Transaction injected.")
        print(f"  - Original Fork Block: {fork_block_number}")
        print(f"  - Injected in Block:   {new_block_number} (Fork Block + 1)")
        print(f"  - Tx Hash:             {tx_receipt['transactionHash'].hex()}")

    except Exception as e:
        print(f"\n❌ Failed to inject transaction: {e}")

if __name__ == "__main__":
    main()
