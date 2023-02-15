from kyc.core.CandidateBase import CandidateBase
from kyc.core.CandidateLoader import CandidateLoader
from kyc.core.CandidateValidator import CandidateValidator
from kyc.core.CandidateValidatorNames import CandidateValidatorNames


class Candidate(
    CandidateBase,
    CandidateLoader,
    CandidateValidator,
    CandidateValidatorNames,
):
    pass
