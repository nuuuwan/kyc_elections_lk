from kyc import Candidate

if __name__ == '__main__':
    Candidate.list_and_store_all()
    Candidate.validate_repeated_names()
    Candidate.validate_coverage()
    Candidate.store_by_lg()
