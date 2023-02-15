from utils import Log, TSVFile
from gig import Ent
log = Log('CandidateValidatorNames')


class CandidateValidatorNames:
    MAX_N_NAMES_REPEATED_IN_LG = 2
    @classmethod
    def get_name_to_candidates(cls):
        candidates = cls.list_all()
        name_to_candidates = {}
        for candidate in candidates:
            if candidate.name not in name_to_candidates:
                name_to_candidates[candidate.name] = []
            name_to_candidates[candidate.name].append(candidate)
        return name_to_candidates

    @classmethod
    def validate_repeated_names(cls):
        name_to_candidates = cls.get_name_to_candidates()

        d_list = []
        n_names = len(name_to_candidates)
        n_names_repeated = 0
        for name, candidates in sorted(
            name_to_candidates.items(),
            key=lambda t: len(t[1]),
        ):
            if len(candidates) == 1:
                continue
            n_names_repeated += 1
            d_list += [candidate.to_dict() for candidate in candidates]

            if len(candidates) < 4:
                continue

            log.warn(f'({len(candidates)}) {name}')

        message = f'{n_names_repeated}/{n_names} names repeated at least once'
        log.debug(message) if n_names_repeated == 0 else log.error(message)

        d_list = sorted(d_list, key=lambda d: d['district_id'])
        report_path = 'data/report.repeated_names.tsv'
        TSVFile(report_path).write(d_list)
        log.info(f'Wrote {report_path}')

    @classmethod
    def lg_to_name_to_candidates(cls):
        candidates = cls.list_all()
        idx = {}
        for candidate in candidates:
            lg_id = candidate.lg_id
            name = candidate.name
            if lg_id not in idx:
                idx[lg_id] = {}
            if name not in idx[lg_id]:
                idx[lg_id][name] = []
            idx[lg_id][name].append(candidate)
        return idx

    @classmethod
    def validate_repeated_names_in_lg(cls):
        idx = cls.lg_to_name_to_candidates()
        for lg_id, name_to_candidates in sorted(
            idx.items(),
            key=lambda item: item[0],
        ):
            n_names = len(name_to_candidates)
            n_names_repeated = 0
            for name, candidates in name_to_candidates.items():
                n = len(candidates)
                if n == 1:
                    continue
                n_names_repeated += 1
            if n_names_repeated > cls.MAX_N_NAMES_REPEATED_IN_LG:
                lg_ent = Ent.from_id(lg_id)
                lg_name = lg_ent.name
                log.error(f'{n_names_repeated}/{n_names}: {lg_id} {lg_name}')
            
