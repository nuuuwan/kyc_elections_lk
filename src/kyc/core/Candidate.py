from kyc.core.CandidateBase import CandidateBase
from kyc.core.CandidateLoader import CandidateLoader


class Candidate(CandidateBase, CandidateLoader):
    pass


if __name__ == '__main__':
    Candidate.list_and_store_all()
