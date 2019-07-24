#from ESC import Candidate
from Transaction import Transaction
import datetime



class DistrictSmartContract:
    def __init__(self, cList, distIP):
        self.candidateList = cList
        # self.startDate = start
        # self.endDate = end
        self.distIP = distIP
        self.transId = 0
        self.voteCount = dict({})
        self.partyCount = dict({})

        for i in range(len(self.candidateList)):
            self.voteCount[self.candidateList[i].candidate_id] = 0
            self.partyCount[self.candidateList[i].party_id] = 0

    def getCandidates(self):
        return self.candidateList



    def validateCandidate(self, candId):
        for i in range(len(self.candidateList)):
            if candId == self.candidateList[i].candidate_id:
                return True
        return False

    # def validateDate(self, currentDate):
    #     if self.startDate <= currentDate <= self.endDate:
    #         return True
    #     return False

    def returnResults(self):
        return voteCount, partyCount

    def castVote(self, candId):
        if not self.validateCandidate(candId):
            return False, None
        # if not self.validateDate(datetime.date.today()):
        #     return False, None

        transaction = Transaction(self.transId, -1, candId)
        self.validVote(candId)
        return True, transaction, self.voteCount

        # Vote is valid.
#ISSUE WITH PARTY COUNT
    def validVote(self, candId):

        self.transId += 1
        self.voteCount[candId] += 1

        self.partyCount[self.candidateList[candId].party_id] += 1
