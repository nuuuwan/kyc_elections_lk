import os
import random
import time

from utils import Log, TSVFile

log = Log('HomePagePipeline')


def sleep(min_sleep=1, sleep_span=5):
    t_sleep = min_sleep + sleep_span * random.random()
    time.sleep(t_sleep)
    log.debug(f'😴: Sleeping for {t_sleep:.2f} s')


class HomePagePipeline:
    MAX_TIME_WAIT_AFTER_SCRAPE_LG = 5
    MAX_TIME_WAIT_AFTER_SCRAPE_DISTRICT = 5
    MAX_INCR_WAIT_AFTER_SELECT_LG = 5

    def scrape_party(self, district_name, lg_name, party_name):
        self.select_party(party_name)

        fptp_candidate_list = self.fptp_candidate_list
        pr_candidate_list = self.pr_candidate_list

        dir_lg = os.path.join('data', district_name, lg_name)
        if not os.path.exists(dir_lg):
            os.system(f'mkdir -p "{dir_lg}"')

        fptp_file_path = os.path.join(dir_lg, f'{party_name}.fptp.tsv')
        TSVFile(fptp_file_path).write(fptp_candidate_list)
        n = len(fptp_candidate_list)
        log.debug(f'Saved {n} FPTP candidates to {fptp_file_path}')

        pr_file_path = os.path.join(dir_lg, f'{party_name}.pr.tsv')
        TSVFile(pr_file_path).write(pr_candidate_list)
        n = len(pr_candidate_list)
        log.debug(f'Saved {n} PR candidates to {pr_file_path}')

    def scrape_lg(self, district_name, lg_name):
        dir_lg = os.path.join('data', district_name, lg_name)
        if os.path.exists(dir_lg):
            log.debug(f'Skipping {district_name}/{lg_name}')
            return
        log.info(f'Scraping {district_name}/{lg_name}')

        self.select_lg(lg_name)
        sleep(2, self.MAX_INCR_WAIT_AFTER_SELECT_LG)

        self.click_captcha()
        self.click_display()

        for party_name in self.party_names:
            self.scrape_party(district_name, lg_name, party_name)

        self.click_back()
        self.select_district(district_name)
        sleep(1, self.MAX_TIME_WAIT_AFTER_SCRAPE_LG)

    def scrape_district(self, district_name):
        self.open()
        self.select_lang()

        self.select_district(district_name)
        for lg_name in self.lg_names:
            self.scrape_lg(district_name, lg_name)

        sleep(1, self.MAX_TIME_WAIT_AFTER_SCRAPE_DISTRICT)
        self.quit()
