from utils import Directory, Log, TSVFile

log = Log('CandidateLoader')


class CandidateLoader:
    DIR_DATA = 'data'

    @classmethod
    def from_fpfp_file(cls, file):
        district_name, lg_name = file.path.split('/')[-3:-1]
        data_list = TSVFile(file.path).read()
        candidates = []
        for data in data_list:
            candidate = cls(
                district_name, lg_name, data['ward'], data['name']
            )
            candidates.append(candidate)
        return candidates

    @classmethod
    def from_pr_file(cls, file):
        district_name, lg_name = file.path.split('/')[-3:-1]
        data_list = TSVFile(file.path).read()
        candidates = []
        for data in data_list:
            candidate = cls(district_name, lg_name, None, data['name'])
            candidates.append(candidate)
        return candidates

    @classmethod
    def from_file(cls, file):
        if file.name.endswith('.fptp.tsv'):
            return cls.from_fpfp_file(file)
        elif file.name.endswith('.pr.tsv'):
            return cls.from_pr_file(file)
        else:
            raise Exception('Unknown file type: ' + file)

    @classmethod
    def list_from_dir_lg(cls, dir_lg):
        dir_lg.name
        candidates = []
        for file in dir_lg.children:
            candidates += cls.from_file(file)
        return candidates

    @classmethod
    def list_from_dir_district(cls, dir_district):
        district_n_lgs = 0
        candidates = []
        for dir_lg in dir_district.children:
            district_n_lgs += 1
            candidates += cls.list_from_dir_lg(dir_lg)
        log.debug(f'Loaded {district_n_lgs} lgs for {dir_district.name}')
        return candidates, district_n_lgs

    @classmethod
    def list_all(cls):
        candidates = []
        n_districts = 0
        n_lgs = 0
        for dir_district in Directory(cls.DIR_DATA).children:
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
