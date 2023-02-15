import os

from utils import Log, TSVFile

from kyc.core.Candidate import Candidate

log = Log('HomePagePipeline')


class HomePagePipeline:
    DIR_DATA = 'data/scraped_data'
    MAX_TIME_WAIT_AFTER_SCRAPE_LG = 5
    MAX_TIME_WAIT_AFTER_SCRAPE_DISTRICT = 5
    MAX_INCR_WAIT_AFTER_SELECT_LG = 5
    MAX_TIME_WAIT_AFTER_SCRAPE_PARTY = 1

    def scrape_party(self, district_name, lg_name, party_name):
        self.select_party(party_name)

        fptp_candidate_list = self.fptp_candidate_list
        pr_candidate_list = self.pr_candidate_list

        dir_lg = os.path.join(self.DIR_DATA, district_name, lg_name)
        if not os.path.exists(dir_lg):
            os.system(f'mkdir -p "{dir_lg}"')

        fptp_file_path = os.path.join(dir_lg, f'{party_name}.fptp.tsv')
        if fptp_candidate_list:
            TSVFile(fptp_file_path).write(fptp_candidate_list)
        n_fptp = len(fptp_candidate_list)

        pr_file_path = os.path.join(dir_lg, f'{party_name}.pr.tsv')
        if pr_candidate_list:
            TSVFile(pr_file_path).write(pr_candidate_list)
        n_pr = len(pr_candidate_list)
        n_total = n_fptp + n_pr
        party_name_clean = Candidate.clean_party(party_name)
        log.debug(f'{party_name_clean}: {n_fptp} + {n_pr} = {n_total} ')

        self.sleep(0.5, self.MAX_TIME_WAIT_AFTER_SCRAPE_PARTY)

    def scrape_lg(self, district_name, lg_name):
        dir_lg = os.path.join(self.DIR_DATA, district_name, lg_name)
        lg_name_clean = Candidate.clean_lg_name(lg_name)
        if os.path.exists(dir_lg):
            log.debug(f'Skipping {lg_name_clean}')
            return
        msg = f'Scraping {lg_name_clean}'
        log.info(msg)

        self.select_lg(lg_name)
        self.sleep(2, self.MAX_INCR_WAIT_AFTER_SELECT_LG)
        self.say(msg)

        self.click_captcha()
        self.click_display()

        for party_name in self.party_names:
            try:
                self.scrape_party(district_name, lg_name, party_name)
            except Exception as e:
                log.error(f'Error scraping {party_name}: {e}')

        self.click_back()
        self.select_district(district_name)
        self.sleep(1, self.MAX_TIME_WAIT_AFTER_SCRAPE_LG)

    def scrape_district(self, district_name):
        self.open()
        self.select_lang()

        self.select_district(district_name)
        for lg_name in self.lg_names:
            self.scrape_lg(district_name, lg_name)

        self.sleep(1, self.MAX_TIME_WAIT_AFTER_SCRAPE_DISTRICT)
        self.quit()
