from hashlib import sha256


def serializeSHA256(text):
    return sha256(text.encode("utf-8")).hexdigest()


def littleEndian(string):
    splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
    splited.reverse()
    return "".join(splited)


def generateMerkleRoot(transactions):
    hashes = []
    for t in range(len(transactions)):
        tx = transactions[t]
        hashes.append(
            serializeSHA256(
                littleEndian(hex(tx['timestamp'])) + littleEndian(tx['sender']) + littleEndian(tx['receiver']) +
                littleEndian(hex(tx['amount'])) + littleEndian(hex(tx['fee']))))

    def innerRecurse(hashes):
        parents = []
        i = 0
        while i < len(hashes):
            l = r = hashes[i]
            if i+1 < len(hashes):
                r = hashes[i+1]
            parents.append(serializeSHA256(l+r))
            i += 2
        if len(parents) > 1:
            return innerRecurse(parents)
        else:
            return parents[0]

    if len(hashes) > 0:
        return innerRecurse(hashes=hashes)
    else:
        return ""
