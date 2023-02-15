from kyc.scraper.HomePage import HomePage

def main():
    district_name = 'Nuwaraeliya'

    home_page = HomePage()
    home_page.scrape_district(district_name)


if __name__ == '__main__':
    main()
