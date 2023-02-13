from utils import Log

from kyc.scraper.HomePageBase import HomePageBase
from kyc.scraper.HomePagePipeline import HomePagePipeline

log = Log('HomePage')


class HomePage(HomePageBase, HomePagePipeline):
    pass


def main():
    district_name = 'Kandy'

    home_page = HomePage()
    home_page.scrape_district(district_name)
    home_page.quit()


if __name__ == '__main__':
    main()
