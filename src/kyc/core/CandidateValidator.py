from utils import Log

log = Log('CandidateValidator')


class CandidateValidator:
    @classmethod
    def validate_repeated_names(cls):
        candidates = cls.list_all()
        name_to_candidates = {}
        for candidate in candidates:
            if candidate.name not in name_to_candidates:
                name_to_candidates[candidate.name] = []
            name_to_candidates[candidate.name].append(candidate)

        for name, candidates in name_to_candidates.items():
            if len(candidates) > 1:
                log.warn(f'Name {name} repeated in {len(candidates)} rows')
