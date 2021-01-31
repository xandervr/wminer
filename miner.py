from hashlib import sha256
import http.client
import json
import sys
from models.block import Block
from models.helpers import generateMerkleRoot
from time import time

MAX_NONCE = 100000000000


def littleEndian(string):
    splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
    splited.reverse()
    return "".join(splited)


class Miner:
    def __init__(self):
        self.version = ''
        self.previous_hash = ''
        self.difficulty = ''
        self.block_size = 512000
        self.block_reward = 0
        self.miner_address = ''
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

    def mineBlock(self, template: str, transactions):
        nonce = 1
        start = time()
        while nonce < MAX_NONCE:
            hash = sha256(f"{template}{littleEndian(hex(nonce))}".encode('utf-8')).hexdigest()
            # print(hash)
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
            conn = http.client.HTTPConnection('localhost', 8000)
            conn.request('GET', '/transactions')
            response = conn.getresponse()
            data = response.read().decode()
            transactions = json.loads(data)
            conn.close()
            return transactions
        except Exception as e:
            print(e)

    def getChainInfo(self):
        try:
            conn = http.client.HTTPConnection('localhost', 8000)
            conn.request('GET', '/info')
            response = conn.getresponse()
            data = response.read().decode()
            info = json.loads(data)
            conn.close()
            return info
        except Exception as e:
            print(e)

    def sendBlock(self, json: bytes):
        try:
            conn = http.client.HTTPConnection('localhost', 8000)
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


m = Miner()
m.startMiner()
