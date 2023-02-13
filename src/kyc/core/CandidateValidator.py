from gig import Ent, EntType
from utils import Log, TSVFile

log = Log('CandidateValidator')
DELIM_ITEMS = '\n\t ❌ '


class CandidateValidator:
    MIN_PARTIES_PER_LG = 4

    @classmethod
    def get_idx(cls):
        candidates = cls.list_all()
        idx = {}
        for candidate in candidates:
            district_id = candidate.district_id
            lg_id = candidate.lg_id
            party_name = str(candidate.party_name)
            if district_id not in idx:
                idx[district_id] = {}
            if lg_id not in idx[district_id]:
                idx[district_id][lg_id] = {}
            if party_name not in idx[district_id][lg_id]:
                idx[district_id][lg_id][party_name] = []
            idx[district_id][lg_id][party_name].append(candidate)
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
    def validate_coverage_for_district(cls, district_id, lg_idx, lg_ent_idx):
        actual_lg_ids = set(lg_idx.keys())

        valid_lg_ids = []
        for lg_id in actual_lg_ids:
            n_party_name = len(lg_idx[lg_id].keys())
            if n_party_name >= cls.MIN_PARTIES_PER_LG:
                valid_lg_ids.append(lg_id)
        actual_lg_ids = set(valid_lg_ids)

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
        missing_lg_names = DELIM_ITEMS.join(
            [lg_ent_idx[lg_id].name for lg_id in missing_lg_ids]
        )
        msg = f'{district_id} {n_missing_lg_ids}/{n_lgs_expected} missing' + (
            f'{DELIM_ITEMS}{str(missing_lg_names)}' if missing_lg_ids else ''
        )
        log.debug(msg) if n_missing_lg_ids == 0 else log.error(msg)
        return d

    @classmethod
    def validate_coverage(cls):
        district_to_lg_ent_idx = cls.get_district_to_lg_ent_idx()
        idx = cls.get_idx()
        d_list = []
        for district_id, lg_idx in idx.items():
            d = cls.validate_coverage_for_district(
                district_id, lg_idx, district_to_lg_ent_idx[district_id]
            )
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
        for name, candidates in sorted(
            name_to_candidates.items(),
            key=lambda t: len(t[1]),
        ):
            if len(candidates) == 1:
                continue
            n_names_repeated += 1
            log.warn(f'({len(candidates)}) {name}')
            d_list += [candidate.to_dict() for candidate in candidates]

        message = f'{n_names_repeated}/{n_names} names repeated at least once'
        log.debug(message) if n_names_repeated == 0 else log.error(message)

        d_list = sorted(d_list, key=lambda d: d['district_id'])
        report_path = 'data/reported_repeated_names.csv'
        TSVFile(report_path).write(d_list)
        log.info(f'Wrote {report_path}')
