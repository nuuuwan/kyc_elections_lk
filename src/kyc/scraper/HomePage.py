from utils import Log

from kyc.scraper.DISTRICT_NAMES import DISTRICT_NAMES
from kyc.scraper.HomePageBase import HomePageBase
from kyc.scraper.HomePagePipeline import HomePagePipeline

log = Log('HomePage')


class HomePage(HomePageBase, HomePagePipeline):
    pass


def main():
    district_name = DISTRICT_NAMES[0]

    home_page = HomePage()
    try:
        home_page.scrape_district(district_name)
    except BaseException as e:
        log.error(e)
    finally:
        home_page.quit()


if __name__ == '__main__':
    main()
