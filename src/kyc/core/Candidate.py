from kyc.core.CandidateBase import CandidateBase
from kyc.core.CandidateLoader import CandidateLoader
from kyc.core.CandidateValidator import CandidateValidator


class Candidate(CandidateBase, CandidateLoader, CandidateValidator):
    pass
