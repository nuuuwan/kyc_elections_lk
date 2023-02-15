from gig import Ent, EntType
from utils import Log, TSVFile

from kyc.core.EXCLUDE_LG_IDS import EXCLUDE_LG_IDS

log = Log('CandidateValidator')
DELIM_ITEMS = '\n\t'
ICON_GOOD = '✅'
ICON_MEH = '🟠'
ICON_BAD = '❌'


class CandidateValidator:
    MIN_PARTIES_PER_LG = 4
    MIN_WARD_NAME_LEN = 4

    @classmethod
    def get_idx(cls):
        candidates = cls.list_all()
        idx = {}

        for candidate in candidates:
            district_id = candidate.district_id
            lg_id = candidate.lg_id
            party = str(candidate.party)
            if district_id not in idx:
                idx[district_id] = {}
            if lg_id not in idx[district_id]:
                idx[district_id][lg_id] = {}
            if party not in idx[district_id][lg_id]:
                idx[district_id][lg_id][party] = []
            idx[district_id][lg_id][party].append(candidate)
        return idx

    @staticmethod
    def get_district_to_lg_ent_idx():
        lg_ents = Ent.list_from_type(EntType.LG)
        idx = {}
        for ent in lg_ents:
            lg_id = ent.id
            if lg_id in EXCLUDE_LG_IDS:
                continue

            district_id = ent.district_id

            if district_id not in idx:
                idx[district_id] = {}
            idx[district_id][lg_id] = ent
        return idx

    @classmethod
    def get_actual_valid_lg_ids(cls, lg_idx, actual_lg_ids):
        valid_lg_ids = []
        for lg_id in actual_lg_ids:
            n_party_name = len(lg_idx[lg_id].keys())
            if n_party_name >= cls.MIN_PARTIES_PER_LG:
                valid_lg_ids.append(lg_id)
        return set(valid_lg_ids)

    @classmethod
    def validate_coverage_for_district(cls, district_id, lg_idx, lg_ent_idx):
        actual_lg_ids = set(lg_idx.keys())
        actual_valid_lg_ids = cls.get_actual_valid_lg_ids(
            lg_idx, actual_lg_ids
        )

        expected_lg_ids = set(lg_ent_idx.keys())
        missing_lg_ids = expected_lg_ids - actual_valid_lg_ids

        n_lgs_actual = len(actual_valid_lg_ids)
        n_lgs_expected = len(expected_lg_ids)

        d = dict(
            district_id=district_id,
            n_lgs_actual=n_lgs_actual,
            n_lgs_expected=n_lgs_expected,
        )

        msg = ''
        if missing_lg_ids:
            for lg_id in expected_lg_ids:
                icon = ICON_BAD
                if lg_id in actual_valid_lg_ids:
                    icon = ICON_GOOD
                elif lg_id in actual_lg_ids:
                    icon = ICON_MEH

                msg += DELIM_ITEMS + icon + ' ' + lg_ent_idx[lg_id].name
            msg += '\n'
        msg += f'{district_id} {n_lgs_actual}/{n_lgs_expected} Done'
        log.error(msg) if missing_lg_ids else log.debug(msg)
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
        report_path = 'data/report.coverage.tsv'
        TSVFile(report_path).write(d_list)
        log.info(f'Wrote {report_path}')
