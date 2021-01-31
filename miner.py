from hashlib import sha256
import http.client
import json
import sys
from models.block import Block
from models.helpers import generateMerkleRoot
from time import time
from math import floor
import argparse

MAX_NONCE = 100000000000


def littleEndian(string):
    splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
    splited.reverse()
    return "".join(splited)


class Miner:
    def __init__(self, miner_address: str, node_host: str, node_port: int):
        self.version = ''
        self.previous_hash = ''
        self.difficulty = ''
        self.block_size = 512000
        self.block_reward = 0
        self.miner_address = miner_address
        self.node_host = node_host
        self.node_port = node_port
        pass

    def loadChainInfo(self, version: str, previous_hash: str, difficulty: int, block_size: int, block_reward: int):
        self.version = version
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.block_size = block_size
        self.block_reward = block_reward

    def generateBaseString(self, merkle_root):
        return self.version + littleEndian(self.previous_hash) + littleEndian(merkle_root) + littleEndian(
            hex(self.difficulty))

    def assembleBlock(self, transactions):
        idx = 0
        totalFee = 0
        chosenTransactions = []
        coinbaseTransaction = {
            'timestamp': int(time()),
            'sender': 'coinbase',
            'receiver': self.miner_address,
            'amount': 0,
            'fee': 0,
            'message': '',
            'signature': '',
            'pubkey': ''
        }
        self.block_size -= sys.getsizeof(coinbaseTransaction) + sys.getsizeof(float)
        while idx < len(transactions) and self.block_size >= sys.getsizeof(coinbaseTransaction):
            tx = transactions[idx]
            totalFee += tx['fee']
            self.block_size -= sys.getsizeof(tx)
            chosenTransactions.append(tx)
            idx += 1
        coinbaseTransaction['amount'] = self.block_reward + totalFee
        chosenTransactions.insert(0, coinbaseTransaction)
        merkle_root = generateMerkleRoot(chosenTransactions)
        base_string = self.generateBaseString(merkle_root)
        return (base_string, chosenTransactions)

    def calculateHashrate(self, hashes, time):
        if time == 0:
            time = 1

        def round(num):
            return floor(num * 100) / 100

        hashrate = hashes/time
        formatted = ""
        if hashrate >= 1000 and hashrate < 1000 * 1000:

            formatted = f"{round(hashrate / 1000)} Kh/s     "
        elif hashrate < 1000:
            formatted = f"{round(hashrate)} h/s     "
        elif hashrate >= 1000 * 1000 and hashrate < 1000 * 1000 * 1000:
            formatted = f"{round(hashrate / 1000 / 1000)} Mh/s      "

        print(formatted, end='\r')

    def mineBlock(self, template: str, transactions):
        nonce = 1
        start = time()
        hash_count = 0
        while nonce < MAX_NONCE:
            hash = sha256(f"{template}{littleEndian(hex(nonce))}".encode('utf-8')).hexdigest()
            hash_count += 1
            intermediate_time = time() - start
            self.calculateHashrate(hash_count, intermediate_time)
            if int(hash, 16) < self.difficulty:
                end = str(time() - start)
                print(f"FOUND HASH: {hash} NONCE: {nonce} in {end} seconds")
                block = {
                    "transactions": transactions,
                    "nonce": nonce
                }
                self.sendBlock(json.dumps(block))
                break
            else:
                nonce += 1

    def getTransactions(self):
        try:
            conn = http.client.HTTPConnection(self.node_host, self.node_port)
            conn.request('GET', '/transactions')
            response = conn.getresponse()
            data = response.read().decode()
            transactions = json.loads(data)
            conn.close()
            return transactions
        except Exception as e:
            print(e)

    def getChainInfo(self, init=False):
        try:
            conn = http.client.HTTPConnection(self.node_host, self.node_port)
            conn.request('GET', '/info')
            response = conn.getresponse()
            data = response.read().decode()
            info = json.loads(data)
            conn.close()
            if init:
                print(f"[CONNECTED] {self.node_host}:{self.node_port}")
            return info
        except Exception as e:
            print(f"[ERROR] Error connecting to {self.node_host}:{self.node_port}")
            # print(e)

    def sendBlock(self, json: bytes):
        try:
            conn = http.client.HTTPConnection(self.node_host, self.node_port)
            headers = {'Content-type': 'application/json'}
            conn.request('POST', '/blocks', json, headers)
            response = conn.getresponse()
            conn.close()
            print(response.status)
            print(response.read().decode())
            if response.status == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def startMiner(self):
        chain_info = self.getChainInfo(True)
        while True:
            chain_info = self.getChainInfo()
            if chain_info is None:
                break
            self.loadChainInfo(
                chain_info['version'],
                chain_info['previous_hash'],
                chain_info['difficulty'],
                chain_info['block_size'],
                chain_info['block_reward'])
            txs = m.getTransactions()
            (template, chosenTxs) = self.assembleBlock(txs)
            self.mineBlock(template, chosenTxs)


parser = argparse.ArgumentParser(description='Wminer for WSB blockchain')
parser.add_argument('--address', type=str, required=True, help='Wallet address')
parser.add_argument('--host', type=str, required=False, default='localhost', help='Node host')
parser.add_argument('--port', type=int, required=False, default=8000, help='Wallet port')
args = parser.parse_args()

m = Miner(args.address, args.host, args.port)
m.startMiner()
