import os
import re

from gig import Ent, EntType
from utils import Directory, JSONFile, Log, TSVFile

from kyc.core.DISTRICT_TO_LG_NAME_TO_ID import DISTRICT_TO_LG_NAME_TO_ID

log = Log('CandidateLoader')


class CandidateLoader:
    DIR_DATA = 'data/scraped_data'
    CANDIDATES_PATH = os.path.join(DIR_DATA, 'candidates.tsv')
    MIN_CANDIDATES_PER_LG = 5

    @classmethod
    def clean_party(cls, party_name):
        party_name_only = party_name.partition('-')[-1].strip()
        words = party_name_only.split(' ')
        return ''.join([word[0] for word in words])

    @classmethod
    def clean_ward_name(cls, x):
        if str(x) == 'None':
            return 0, 'PR List'

        x = x.replace(' - ', '-')
        x = re.sub(r'\s+', ' ', x).strip()
        words = x.split('-')
        ward_num = (int)(words[0])
        ward_name = '-'.join(words[1:])
        return ward_num, ward_name

    @classmethod
    def clean_lg_name(cls, lg_name):
        return (
            lg_name.replace('Municipal Council', 'MC')
            .replace('Urban Council', 'UC')
            .replace('Pradeshiya Sabha', 'PS')
        )

    @classmethod
    def get_lg_id(cls, district_id, dir_lg):
        lg_name = cls.clean_lg_name(dir_lg.name)

        if (
            district_id in DISTRICT_TO_LG_NAME_TO_ID
            and lg_name in DISTRICT_TO_LG_NAME_TO_ID[district_id]
        ):
            return DISTRICT_TO_LG_NAME_TO_ID[district_id][lg_name]

        cand_lg_ents = Ent.list_from_name_fuzzy(
            lg_name,
            EntType.LG,
            district_id[2:],  # HACK to fix bug in ent.is_parent_id
        )
        if len(cand_lg_ents) == 0:
            district_num = district_id[3:]
            print(f"'{lg_name}': 'LG-{district_num}xxx',")
            return district_num

            # raise Exception(f'No LG found for {lg_name} ({district_id})')

        else:
            return cand_lg_ents[0].id

    @classmethod
    def from_file(cls, district_id, lg_id, file):
        data_list = TSVFile(file.path).read()
        candidates = []
        party_name = '.'.join(file.name.split('.')[:-2])
        for data in data_list:
            ward_num, _ = cls.clean_ward_name(data.get('ward', 'None'))

            candidate = cls(
                district_id,
                lg_id,
                ward_num,
                cls.clean_party(party_name),
                data['name'],
            )
            if not candidate.is_valid:
                continue
            candidates.append(candidate)
        return candidates

    @classmethod
    def list_from_dir_lg(cls, district_id, dir_lg):
        lg_id = cls.get_lg_id(district_id, dir_lg)

        candidates = []
        for file in dir_lg.children:
            candidates += cls.from_file(district_id, lg_id, file)

        n_candidates = len(candidates)
        if n_candidates < cls.MIN_CANDIDATES_PER_LG:
            log.error(f'{lg_id} has only {n_candidates} candidates. Deleting')
            os.system(f'rm -r "{dir_lg.path}"')

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

        return candidates, district_n_lgs

    @classmethod
    def list_all_parse(cls):
        candidates = []
        n_districts = 0
        n_lgs = 0
        for child in Directory(cls.DIR_DATA).children:
            if not isinstance(child, Directory):
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
            + str(d['ward_num'] + 10_000)
            + d['party']
            + d['name'],
        )

        TSVFile(cls.CANDIDATES_PATH).write(d_list)
        log.info(
            f'Stored {len(d_list):,} candidates to {cls.CANDIDATES_PATH}'
        )

        JSONFile(cls.CANDIDATES_PATH[:-4] + '.json').write(d_list)

    @classmethod
    def list_all(cls):
        d_list = TSVFile(cls.CANDIDATES_PATH).read()
        return [cls.from_dict(d) for d in d_list]

    @classmethod
    def get_lg_to_candidates(cls):
        candidates = cls.list_all()
        idx = {}
        for candidate in candidates:
            lg_id = candidate.lg_id
            if lg_id not in idx:
                idx[lg_id] = []
            idx[lg_id].append(candidate)
        return idx

    @classmethod
    def store_by_lg(cls):
        idx = cls.get_lg_to_candidates()
        for lg_id, candidates in idx.items():
            d_list = [candidate.to_dict() for candidate in candidates]
            d_list = sorted(
                d_list,
                key=lambda d: str(d['ward_num'] + 1_000) + d['party'] + d['name'],
            )
            lg_data_path = os.path.join(
                'data',
                'candidates_by_lg',
                f'{lg_id}.json',
            )
            JSONFile(lg_data_path).write(d_list)
