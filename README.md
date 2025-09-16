# Ethereum Fork Simulation & Validation Toolkit 🛠️

This toolkit provides a set of Python scripts designed for high-fidelity testing and simulation of Ethereum smart contracts. It allows you to validate a local Anvil fork against the mainnet, inject new transactions, inspect block contents, and simulate transactions within historical blocks (WIP).

## Scripts Overview

This toolkit contains four primary scripts:

  * **`1_replay_engine.py` (The Validator 🧐):** Compares your local fork against the mainnet to ensure transaction outcomes are identical, calculating a "Fidelity Score" for accuracy.
  * **`2_transaction_injector.py` (The Actor 🧑‍💻):** Injects a new, custom transaction onto your local fork to simulate user activity and set up test states.
  * **`3_block_viewer.py` (The Inspector 🔬):** A utility to look inside any block on your local node and see its contents, including a full list of existing and new injected transactions.
  * **`simulation_engine.py` (WORK IN PROGRESS):** An advanced script to simulate what *would have happened* if your transaction had been included in a specific historical block.

-----

## A Note on Transaction Order

You might notice that the output of the `replay_engine` shows transactions in a different order than a block explorer like Etherscan. This is expected and reflects two different ways of viewing the same data.

  * **Etherscan (Presentation View):** Block explorers are designed for human readability. They typically show the **most recent transaction at the top** of the list, much like a social media feed. This is convenient for quickly seeing the latest activity.
  * **Replay Engine (Chronological View):** The script reads the `transactions` array directly from the block data as it's stored on the blockchain. This array is ordered **chronologically**, based on when each transaction was processed and included by the miners. It starts at index `0` (the first transaction in the block) and goes to the last.

Think of it like this: Etherscan is showing you a news feed (latest first), while the script is reading a chapter in a book (telling the story from beginning to end). Both are correct, but they serve different purposes. Our script needs the chronological order to accurately replay the block's events as they originally happened.

-----

## Step-by-Step Tutorial

This guide will walk you through setting up the project and running a complete validation and injection workflow.

### Step 1: Project Setup

First, let's get your environment and dependencies ready.

1.  **Clone the Repository (or download the files):** Get the script files into a local directory on your machine.

2.  **Create and Activate a Python Virtual Environment:** This keeps your project dependencies isolated.

    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (on macOS/Linux)
    source venv/bin/activate

    # On Windows, use:
    # venv\Scripts\activate
    ```


3.  **Install Dependencies:** Run the following command in your terminal to install the required packages.

    ```bash
    pip install -r requirements.txt
    ```

### Step 2: Configuration

The scripts need an RPC URL to communicate with the Ethereum mainnet.

1.  **Get an RPC URL:** You'll need one from a node provider like [Infura](https://infura.io/), [Alchemy](https://www.alchemy.com/), or another service like GCP's Blockchain RPC.

2.  **Create a `.env` file:** In the same project directory, create a file named `.env`. This file will securely store your RPC URL where the scripts can access it.

3.  **Add Your URL:** Add the following line to your `.env` file, replacing the placeholder with your actual RPC URL.

    ```
    # .env
    RPC_URL="https://mainnet.infura.io/v3/your-api-key"
    ```


### Step 3: Example Workflow

Now, let's run a full test. We will fork the blockchain, validate it, inject a transaction, and inspect the results.

1.  **Start Your Anvil Fork:**
    Open a **new terminal window** and run the following command. This tells Anvil to create a local copy of the Ethereum blockchain, starting from block `19500000` or any other block of your own choice.

    ```bash
    anvil --fork-url $RPC_URL --fork-block-number 19500000
    ```

    > **Note:** `$RPC_URL` fetches the variable from your environment. If that doesn't work, you can paste the URL directly. Leave this terminal window running.

2.  **Validate the Fork:**
    Now, in your **original terminal** (where your `venv` is active), run the replay engine to check the integrity of the next block.

    ```bash
    python 1_replay_engine.py
    ```

    The script will prompt you for input. Enter the following:

      * Enter the Start Block number: **`19500000`** or less than 19500000
      * Enter Validation Duration (in blocks): **`1`** or more

    The script will process all transactions in block `19500001` and should output a **🏆 Final Fidelity Score: 100.00%**. This confirms your local fork is a perfect replica.

3.  **Inject a New Transaction:**
    Next, run the transaction injector. This will send a new transaction to your local Anvil node, which will mine it into a new block.

    ```bash
    python 2_transaction_injector.py
    ```

    The output will confirm that a transaction was successfully injected into the next block on your local chain (which will be block \#`19500001`, since Anvil starts mining after the fork point).

4.  **Inspect the Blocks:**
    Finally, use the block viewer to see the difference between the original mainnet block and the new one you just created locally.

      * First, inspect the **original** block:

        ```bash
        python 3_block_viewer.py
        ```

        When prompted, enter the block number: **`19500000`**. You will see all the transactions from the real mainnet block.

      * Next, inspect your **new** block:

        ```bash
        python 3_block_viewer.py
        ```

        When prompted, enter the block number: **`19500001`**. You will see the single dummy transaction that you just injected.
