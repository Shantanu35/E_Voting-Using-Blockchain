import requests
from flask import Flask, request
from DSC import DistrictSmartContract
import json
import datetime

app = Flask(__name__)

esc = None
transaction = None
candidate_id = None


# district_id = None


class Candidate:
    def __init__(self, candId, district_id, party_id, candName, partyName):
        self.candidate_id = candId
        self.district_id = district_id
        self.party_id = party_id
        self.candidate_name = candName
        self.party_name = partyName

    def getJson(self):
        return {"candidate_id": self.candidate_id, "district_id": self.district_id, "party_id": self.party_id,
                "candidate_name": self.candidate_name, "party_name": self.party_name}


class ElectionSmartContract:
    def __init__(self, candidateList, distList, distIP, start, end, electionName):
        """Called initially after the EA clicks to Create Election"""
        self.candidateList = candidateList
        self.distList = distList
        self.distIP = distIP
        self.startDate = start
        self.startDate = datetime.datetime.strptime(self.startDate, '%Y-%m-%d').date()
        self.endDate = end
        self.endDate = datetime.datetime.strptime(self.endDate, '%Y-%m-%d').date()
        self.electionName = electionName
        self.districtSmartContract = []
        self.__initiateElection()

    # ISSUE WITH DATE.
    def validateDate(self, currentDate):
        if self.startDate <= currentDate <= self.endDate:
            return True
        return False

    # will be called by the election smart contract
    # ISSUE WITH DATE
    def __initiateElection(self):
        self.__createDistrictSC(self.distList)

    def __createDistrictSC(self, distList):
        distCandidate = dict({})

        for i in range(len(distList)):
            distCandidate[distList[i]] = []

        for i in range(0, len(self.candidateList)):
            # distCandidate[self.candidateList[i].district_id] = []
            distCandidate[self.candidateList[i].district_id].append(self.candidateList[i])

        for i in range(len(distList)):
            districtSC = DistrictSmartContract(distCandidate[distList[i]], self.distIP[i])
            self.districtSmartContract.append(districtSC)

    # will be called by the election smart contract
    def getResults(self):
        voteCount = dict({})
        partyCount = dict({})

        for i in self.candidateList:
            voteCount[i.candidate_id] = 0
            partyCount[i.party_id] = 0

        for i in self.districtSmartContract:
            tempVC, tempPC = i.returnResults()
            for k, v in tempVC.items():
                voteCount[k] += v
            for k, v in tempPC.items():
                partyCount[k] += v

        return voteCount, partyCount

    # def callDistrictSC(self, district_id):
    #     """Each voter after registration will call this to direct to district smart contract"""


@app.route('/election_request', methods=['POST'])
def election_request():
    global esc
    request.get_json()
    json = request.json

    candidateid = json["candidate_id"]
    candidateName = json["candidate_names"]
    cand_districtList = json["candidate_district_id"]
    cand_partyList = json["candidate_party_id"]
    cand_partyNames = json["candidate_party_names"]
    districtList = json["participating_nodes"]
    districtIP = json["districtIP"]
    startDate = json["election_start_date"]
    endDate = json["election_end_date"]
    electionName = json["election_name"]

    print(startDate)
    candidateList = []
    for i in range(len(candidateid)):
        obj = Candidate(int(candidateid[i]), int(cand_districtList[i]), int(cand_partyList[i]), candidateName[i],
                        cand_partyNames[i])
        candidateList.append(obj)
    esc = ElectionSmartContract(candidateList, districtList, districtIP, startDate, endDate, electionName)

    response = {"Status": "ok"}
    return response, '200'


@app.route('/get_candidates', methods=['POST'])
def get_candidates():
    global esc
    # esc = ElectionSmartContract([Candidate(1, 1, 1), Candidate(2, 2, 2), Candidate(3, 1, 3), Candidate(4, 2, 4)],
    #                             [1, 2], ["146.122.195.140:90", "146.122.195.140:91"], '2019-07-20', '2019-07-28', 'Lok Sabha')

    # esc = ElectionSmartContract([Candidate(1, 1, 1, "SJ", "SJ"), Candidate(2, 2, 2, "SJ", "SJ"), Candidate(6, 1, 3, "SJ", "SJ"), Candidate(3, 2, 4, "SJ", "SJ")],
    #                             [1, 2], ["146.122.195.140:90", "146.122.195.140:91"], '2019-07-20', '2019-07-28', 'Lok Sabha')

    request.get_json()
    json = request.json
    districtSC = None
    print("In here.", type(json))
    # district_id = json["district_id"]
    # for i in range(len(esc.distList)):
    #     if esc.distList[i] == district_id:
    #         districtSC = esc.districtSmartContract[i]
    #         break

    district_id = json["district_id"]
    districtSC = esc.districtSmartContract[district_id - 1]
    response = {"candidateList": [c.getJson() for c in districtSC.getCandidates()]}
    return response, 200


@app.route('/validate_vote', methods=['POST'])
def validate_vote():
    global transaction, candidate_id, esc
    request.get_json()
    json = request.json
    districtSC = None
    candidate_id = json["candidate_id"]
    for i in range(len(esc.candidateList)):
        if esc.candidateList[i].candidate_id == candidate_id:
            districtSC = esc.districtSmartContract[esc.candidateList[i].district_id - 1]
    # districtSC = esc.districtSmartContract[esc.candidateList[candidate_id - 1].district_id - 1]

    voted, transaction, voteCount = districtSC.castVote(candidate_id)
    print(type(transaction.getJson()))

    for i in esc.districtSmartContract:
        print(i.voteCount)
    broadcast_variables(voteCount)

    # requests.post("localhost:90", json = transaction.getJson())

    response = {"Status": voted, "Transaction": transaction.getJson()}
    return response, 200


# @app.route('/broadcast_variables', methods=['POST'])
def broadcast_variables(variables):
    global candidate_id, esc
    print(candidate_id)
    distip = None
    for i in range(len(esc.candidateList)):
        if esc.candidateList[i].candidate_id == candidate_id:
            distip = esc.distIP[esc.candidateList[i].district_id - 1]

    for i in esc.distIP:
        if not i == distip:
            response = requests.post('http://' + i + '/receive_variables', json=variables)


@app.route('/receive_variables', methods=['POST'])
def receive_variables():
    global esc
    request.get_json()
    voteCount = dict()
    district_id = None
    for key, value in request.json.items():
        voteCount[int(key)] = value

    print(voteCount)

    for i in range(len(esc.candidateList)):
        if esc.candidateList[i].candidate_id == int(list(voteCount.keys())[0]):
            district_id = esc.candidateList[i].district_id

    # district_id = esc.candidateList[int(list(voteCount.keys())[0]) - 1].district_id
    esc.districtSmartContract[district_id - 1].voteCount = voteCount

    for i in esc.districtSmartContract:
        print(i.voteCount)

    return "SUCCESS", 200


@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    global transaction
    # print(json.dumps(transaction.getJson()))
    # transaction_file = open("transaction_file.json", "w")
    # transaction_file.write(json.dumps(transaction.getJson()))
    # transaction_file.close()

    vote_status = requests.post("http://146.122.195.103:901/add_transaction",
                                files={"transactions": request.files["transaction"],
                                       "public_key": request.files["public_key"],
                                       "signature": request.files["signature"]
                                       })

    # if vote_status:
    #     esc.districtSmartContract[esc.candidateList[candidate_id - 1].district_id - 1].validVote(candidate_id)
    print(vote_status.content)
    response = {"Status": vote_status.content.decode()}
    return response


# WEB SERVER WILL CALL THIS AT THE END OF ELECTIONS
@app.route('/return_results')
def return_results():
    global esc
    if not esc.validateDate(datetime.date.today()):
        voteCount, partyCount = esc.getResults()
        response = {"voteCount": voteCount, "partyCount": partyCount}
        return response, 200
    else:
        response = {"status": -1}
        return response, 400


app.run("146.122.195.140", 91)
