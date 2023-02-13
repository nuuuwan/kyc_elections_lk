from gig import Ent, EntType
from utils import Log, TSVFile

log = Log('CandidateValidator')


class CandidateValidator:
    @classmethod
    def get_idx_by_district_and_lg(cls):
        candidates = cls.list_all()
        idx = {}
        for candidate in candidates:
            district_id = candidate.district_id
            lg_id = candidate.lg_id
            if district_id not in idx:
                idx[district_id] = {}
            if lg_id not in idx[district_id]:
                idx[district_id][lg_id] = []
            idx[district_id][lg_id].append(candidate)
        return idx

    @staticmethod
    def get_district_to_lg_ent_idx():
        lg_ents = Ent.list_from_type(EntType.LG)
        idx = {}
        for ent in lg_ents:
            lg_id = ent.id
            district_id = ent.district_id

            if district_id not in idx:
                idx[district_id] = {}
            idx[district_id][lg_id] = ent
        return idx

    @classmethod
    def validate_coverage(cls):
        district_to_lg_ent_idx = cls.get_district_to_lg_ent_idx()
        idx = cls.get_idx_by_district_and_lg()
        d_list = []
        for district_id, lg_idx in idx.items():
            actual_lg_ids = set(lg_idx.keys())
            lg_ent_idx = district_to_lg_ent_idx[district_id]
            expected_lg_ids = set(lg_ent_idx.keys())
            missing_lg_ids = expected_lg_ids - actual_lg_ids

            n_lgs_actual = len(actual_lg_ids)
            n_lgs_expected = len(expected_lg_ids)

            d = dict(
                district_id=district_id,
                n_lgs_actual=n_lgs_actual,
                n_lgs_expected=n_lgs_expected,
            )

            n_missing_lg_ids = len(missing_lg_ids)
            missing_lg_names = ';'.join(
                [lg_ent_idx[lg_id].name for lg_id in missing_lg_ids]
            )
            msg = (
                f'{district_id} {n_missing_lg_ids}/{n_lgs_expected} missing'
                + f' ({str(missing_lg_names)})'
            )
            log.debug(msg) if n_missing_lg_ids == 0 else log.warn(msg)
            d_list.append(d)

        d_list = sorted(d_list, key=lambda d: d['district_id'])
        report_path = 'data/report_coverage.csv'
        TSVFile(report_path).write(d_list)
        log.info(f'Wrote {report_path}')

    @classmethod
    def validate_repeated_names(cls):
        candidates = cls.list_all()
        name_to_candidates = {}
        for candidate in candidates:
            if candidate.name not in name_to_candidates:
                name_to_candidates[candidate.name] = []
            name_to_candidates[candidate.name].append(candidate)

        d_list = []
        n_names = len(name_to_candidates)
        n_names_repeated = 0
        for name, candidates in name_to_candidates.items():
            if len(candidates) == 1:
                continue
            n_names_repeated += 1
            log.warn(f'Name {name} repeated in {len(candidates)} rows')
            d_list += [candidate.to_dict() for candidate in candidates]

        message = f'{n_names_repeated}/{n_names} names repeated at least once'
        log.debug(message) if n_names_repeated == 0 else log.error(message)

        d_list = sorted(d_list, key=lambda d: d['district_id'])
        report_path = 'data/reported_repeated_names.csv'
        TSVFile(report_path).write(d_list)
        log.info(f'Wrote {report_path}')
