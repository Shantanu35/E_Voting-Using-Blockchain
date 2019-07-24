
class Transaction:
    def __init__(self, transId, blockId, candidateId):
        self.transactionId = transId
        self.blockId = blockId
        self.candidateId = candidateId

    def getJson(self):
        return {"transactionId": self.transactionId, "blocId" : self.blockId, "candidateId" : self.candidateId}