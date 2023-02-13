import random

from utils import Log, mr

from kyc.core.Candidate import Candidate
from kyc.scraper.DISTRICT_NAMES import DISTRICT_NAMES
from kyc.scraper.HomePageBase import HomePageBase
from kyc.scraper.HomePagePipeline import HomePagePipeline

log = Log('HomePage')


class HomePage(HomePageBase, HomePagePipeline):
    pass


def main():
    MAX_THREADS = 5
    district_names = DISTRICT_NAMES
    random.shuffle(district_names)
    district_names = district_names[:MAX_THREADS]

    def worker(district_name):
        home_page = HomePage()
        try:
            home_page.scrape_district(district_name)
        except BaseException as e:
            home_page.quit()
            log.error(e)

    mr.map_parallel(worker, district_names, max_threads=MAX_THREADS)
    Candidate.list_all()


if __name__ == '__main__':
    main()
