import os

from gig import Ent, EntType
from utils import Directory, Log, TSVFile

from kyc.core.LG_NAME_TO_ID import LG_NAME_TO_ID

log = Log('CandidateLoader')


def clean_lg_name(lg_name):
    return (
        lg_name.replace('Municipal Council', 'MC')
        .replace('Urban Council', 'UC')
        .replace('Pradeshiya Sabha', 'PS')
    )


def get_lg_id(district_id, dir_lg):
    lg_name = clean_lg_name(dir_lg.name)

    if lg_name in LG_NAME_TO_ID:
        return LG_NAME_TO_ID[lg_name]

    cand_lg_ents = Ent.list_from_name_fuzzy(
        lg_name,
        EntType.LG,
        district_id[2:],  # HACK to fix bug in ent.is_parent_id
    )
    if len(cand_lg_ents) == 0:
        # district_num = district_id[3:]
        # print(f"'{lg_name}': 'LG-{district_num}xxx',")
        raise Exception(f'No LG found for {lg_name} ({district_id})')
    else:
        return cand_lg_ents[0].id


class CandidateLoader:
    DIR_DATA = 'data'
    CANDIDATES_PATH = os.path.join(DIR_DATA, 'candidates.tsv')

    @classmethod
    def from_file(cls, distrit_id, lg_id, file):
        data_list = TSVFile(file.path).read()
        candidates = []
        party_name = '.'.join(file.name.split('.')[:-2])
        for data in data_list:
            candidate = cls(
                distrit_id,
                lg_id,
                data.get('ward', None),
                party_name,
                data['name'],
            )
            candidates.append(candidate)
        return candidates

    @classmethod
    def list_from_dir_lg(cls, district_id, dir_lg):
        lg_id = get_lg_id(district_id, dir_lg)

        candidates = []
        for file in dir_lg.children:
            candidates += cls.from_file(district_id, lg_id, file)
        return candidates

    @classmethod
    def list_from_dir_district(cls, dir_district):
        district_name = dir_district.name
        district_id = Ent.list_from_name_fuzzy(
            district_name, EntType.DISTRICT
        )[0].id

        district_n_lgs = 0
        candidates = []
        for dir_lg in dir_district.children:
            district_n_lgs += 1
            candidates += cls.list_from_dir_lg(district_id, dir_lg)
        # log.debug(f'Loaded {district_n_lgs} lgs for {district_id}')
        return candidates, district_n_lgs

    @classmethod
    def list_all_parse(cls):
        candidates = []
        n_districts = 0
        n_lgs = 0
        for child in Directory(cls.DIR_DATA).children:
            if child.path == cls.CANDIDATES_PATH:
                continue

            dir_district = child
            n_districts += 1
            district_candidates, district_n_lgs = cls.list_from_dir_district(
                dir_district
            )
            candidates += district_candidates
            n_lgs += district_n_lgs

        n_candidates = len(candidates)
        log.info(
            f'Loaded {n_candidates:,} candidates'
            + f' from {n_lgs} lgs in {n_districts} districts'
        )

        return candidates

    @classmethod
    def list_and_store_all(cls):
        candidates = cls.list_all_parse()
        d_list = [candidate.to_dict() for candidate in candidates]
        d_list = sorted(
            d_list,
            key=lambda d: d['lg_id']
            + str(d['ward_name'])
            + d['party_name']
            + d['name'],
        )

        TSVFile(cls.CANDIDATES_PATH).write(d_list)
        log.info(
            f'Stored {len(d_list):,} candidates to {cls.CANDIDATES_PATH}'
        )

    @classmethod
    def list_all(cls):
        d_list = TSVFile(cls.CANDIDATES_PATH).read()
        return [cls.from_dict(d) for d in d_list]
