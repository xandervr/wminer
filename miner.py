from hashlib import sha256
import http.client
import json
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
        pass

    def loadChainInfo(self, version: str, previous_hash: str, difficulty: int):
        self.version = version
        self.previous_hash = previous_hash
        self.difficulty = difficulty

    def generateBaseString(self, merkle_root):
        return self.version + littleEndian(self.previous_hash) + littleEndian(merkle_root) + littleEndian(
            hex(self.difficulty))

    def mineBlock(self, transactions):
        merkle_root = generateMerkleRoot(transactions)
        base_string = self.generateBaseString(merkle_root)
        nonce = 1
        start = time()
        while nonce < MAX_NONCE:
            hash = sha256(f"{base_string}{littleEndian(hex(nonce))}".encode('utf-8')).hexdigest()
            # print(hash)
            if int(hash, 16) < self.difficulty:
                end = str(time() - start)
                print(f"FOUND HASH: {hash} NONCE: {nonce} in {end} seconds")
                block = {
                    "transactions": list(map(lambda x: x['signature'], transactions)),
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
            self.loadChainInfo(chain_info['version'], chain_info['previous_hash'], chain_info['difficulty'])
            txs = m.getTransactions()
            self.mineBlock(txs)


m = Miner()
m.startMiner()
