from utils import mr

from kyc.scraper.DISTRICT_NAMES import DISTRICT_NAMES
from kyc.scraper.HomePageBase import HomePageBase
from kyc.scraper.HomePagePipeline import HomePagePipeline


class HomePage(HomePageBase, HomePagePipeline):
    pass


if __name__ == '__main__':

    def worker(district_name):
        home_page = HomePage()
        home_page.scrape_district(district_name)

    mr.map_parallel(
        worker,
        DISTRICT_NAMES,
        max_threads=4,
    )
