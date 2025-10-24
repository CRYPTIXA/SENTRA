import sys
import os
import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import config

NHOST_API_URL = config["nhost"]["api_url"]
NHOST_ADMIN_SECRET = config["nhost"]["admin_secret"]

HEADERS = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": NHOST_ADMIN_SECRET
}

class NhostDB:
    def __init__(self):
        self.api_url = NHOST_API_URL
        self.headers = HEADERS

    def execute(self, query, variables=None):
        payload = {"query": query, "variables": variables or {}}
        response = httpx.post(self.api_url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def add_user(self, user_id, whale_threshold):
        query = """
        mutation AddUser($id: String!, $threshold: Int!) {
          insert_users(objects: {id: $id, whale_threshold: $threshold}) {
            affected_rows
          }
        }
        """
        variables = {"id": user_id, "threshold": whale_threshold}
        return self.execute(query, variables)

    def update_threshold(self, user_id, whale_threshold):
        query = """
        mutation UpdateThreshold($id: String!, $threshold: Int!) {
          update_users(where: {id: {_eq: $id}}, _set: {whale_threshold: $threshold}) {
            affected_rows
          }
        }
        """
        variables = {"id": user_id, "threshold": whale_threshold}
        return self.execute(query, variables)

    def add_tracked_wallet(self, user_id, wallet_address):
        query = """
        mutation AddWallet($user_id: String!, $wallet: String!) {
          insert_tracked_wallets(objects: {user_id: $user_id, wallet_address: $wallet}) {
            affected_rows
          }
        }
        """
        variables = {"user_id": user_id, "wallet": wallet_address}
        return self.execute(query, variables)

    def get_tracked_wallets(self, user_id):
        query = """
        query GetWallets($user_id: String!) {
          tracked_wallets(where: {user_id: {_eq: $user_id}}) {
            wallet_address
          }
        }
        """
        variables = {"user_id": user_id}
        result = self.execute(query, variables)
        return [w["wallet_address"] for w in result["data"]["tracked_wallets"]]

    def log_whale_transaction(self, tx_hash, from_address, to_address, amount, token, usd_value, timestamp):
        query = """
        mutation LogTransaction($tx_hash: String!, $from: String!, $to: String!, $amount: numeric!, $token: String!, $usd_value: numeric!, $timestamp: timestamptz!) {
          insert_whale_transactions(objects: {
            tx_hash: $tx_hash,
            from_address: $from,
            to_address: $to,
            amount: $amount,
            token: $token,
            usd_value: $usd_value,
            timestamp: $timestamp
          }) {
            affected_rows
          }
        }
        """
        variables = {
            "tx_hash": tx_hash,
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "token": token,
            "usd_value": usd_value,
            "timestamp": timestamp
        }
        return self.execute(query, variables)
