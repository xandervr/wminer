from .helpers import serializeSHA256, littleEndian
import json
import time


class Block:
    def __init__(self, version, previous_hash, merkle_root, difficulty, nonce, transactions):
        self.version = version
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.timestamp = int(time())
        self.difficulty = difficulty
        self.nonce = nonce
        self.transactions = transactions
        self.hash = self.getHash()

    def __str__(self) -> str:
        return '''
            Version: {}
            Previous hash: {}
            Merkle root: {}
            Timestamp: {}
            Difficulty: {}
            Nonce: {}
            Timestamp: {}
            Hash: {}
            Transactions: {}
            '''.format(self.version, self.previous_hash, self.merkle_root, self.timestamp, self.difficulty, self.nonce,
                       self.timestamp, self.hash, self.transactions)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def getHash(self):
        return serializeSHA256(
            self.version + littleEndian(self.previous_hash) + littleEndian(self.merkle_root) +
            littleEndian(hex(int(self.timestamp))) + littleEndian(hex(self.difficulty)) + littleEndian(hex(self.nonce)))
