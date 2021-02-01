from .helpers import serializeSHA256, littleEndian
import json
import time


class Block:
    def __init__(self, timestamp, version, previous_hash, merkle_root, difficulty, nonce, transactions, height=1):
        self.version = version
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce
        self.transactions = transactions
        self.hash = self.getHash()
        self.height = height

    def __str__(self) -> str:
        return '''
            Height: {}
            Version: {}
            Previous hash: {}
            Merkle root: {}
            Timestamp: {}
            Difficulty: {}
            Nonce: {}
            Timestamp: {}
            Hash: {}
            Transactions: {}
            '''.format(self.height, self.version, self.previous_hash, self.merkle_root, self.timestamp, self.difficulty,
                       self.nonce, self.timestamp, self.hash, self.transactions)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def getHash(self):
        return serializeSHA256(
            self.version + littleEndian(self.previous_hash) + littleEndian(self.merkle_root) + hex(self.timestamp) +
            hex(self.difficulty) + str(self.nonce))
