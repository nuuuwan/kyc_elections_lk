from kyc.scraper.DISTRICT_NAMES import DISTRICT_NAMES
from kyc.scraper.HomePage import HomePage

# TODO


def main():
    district_name = 'Ampara'
    assert district_name in DISTRICT_NAMES

    home_page = HomePage()
    home_page.scrape_district(district_name)


if __name__ == '__main__':
    main()
