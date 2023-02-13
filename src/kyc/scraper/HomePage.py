import random

from kyc.core.Candidate import Candidate
from kyc.scraper.DISTRICT_NAMES import DISTRICT_NAMES
from kyc.scraper.HomePageBase import HomePageBase
from kyc.scraper.HomePagePipeline import HomePagePipeline


class HomePage(HomePageBase, HomePagePipeline):
    pass


if __name__ == '__main__':
    district_names = DISTRICT_NAMES
    random.shuffle(district_names)

    for district_name in district_names:
        Candidate.list_all()
        home_page = HomePage()
        try:
            home_page.scrape_district(district_name)
            Candidate.list_all()
        except BaseException:
            home_page.quit()
            Candidate.list_all()
            break
