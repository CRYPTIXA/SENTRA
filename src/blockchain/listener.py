import asyncio
from web3 import Web3
from config_loader import config
from database.nhost_db import NhostDB
from datetime import datetime

rpc_url = config["rpc_urls"].get("alchemy") or config["rpc_urls"].get("infura")
w3 = Web3(Web3.HTTPProvider(rpc_url))

nhost_db = NhostDB()
WHALE_THRESHOLD = config["whale_threshold_usd"]

async def check_block(block_number):
    block = w3.eth.get_block(block_number, full_transactions=True)
    for tx in block.transactions:
        if tx.value == 0:
            continue
        usd_value = w3.fromWei(tx.value, "ether")  # Placeholder: ideally convert to USD
        if usd_value >= WHALE_THRESHOLD:
            tx_hash = tx.hash.hex()
            from_address = tx["from"]
            to_address = tx["to"]
            amount = w3.fromWei(tx.value, "ether")
            timestamp = datetime.utcfromtimestamp(block.timestamp).isoformat()

            nhost_db.log_whale_transaction(
                tx_hash, from_address, to_address, amount, "ETH", usd_value, timestamp
            )
            print(f"Whale transaction detected: {tx_hash} | {amount} ETH")

async def monitor_chain(start_block=None):
    if start_block is None:
        start_block = w3.eth.block_number

    current_block = start_block
    while True:
        latest_block = w3.eth.block_number
        while current_block <= latest_block:
            await check_block(current_block)
            current_block += 1
        await asyncio.sleep(10)  # Poll every 10 seconds

if __name__ == "__main__":
    asyncio.run(monitor_chain())
