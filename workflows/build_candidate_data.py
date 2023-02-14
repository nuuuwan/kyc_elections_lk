from kyc import Candidate

if __name__ == '__main__':
    Candidate.list_and_store_all()
    Candidate.validate_repeated_names()
    Candidate.validate_coverage()
    Candidate.validate_for_missing_ward_names()
