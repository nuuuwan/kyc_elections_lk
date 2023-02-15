import os
import random
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import Log

from kyc.core.Candidate import Candidate

log = Log('HomePageBase')


def clean(x):
    return re.sub(r'\s+', ' ', x).strip()


class HomePageBase:
    URL = 'https://eservices.elections.gov.lk/pages/ec_ct_KYC_LGA.aspx'
    WAIT_TIME_FOR_DISPLAY_BUTTON_LOAD = 60
    WAIT_TIME_FOR_DISPLAY_BUTTON_LOAD = 30

    @staticmethod
    def sleep(min_sleep=1, sleep_span=5):
        t_sleep = min_sleep + sleep_span * random.random()
        log.debug(f'😴 {t_sleep:.2f} s')
        time.sleep(t_sleep)

    @staticmethod
    def say(text):
        os.system(f'say "{text}"')

    def __init__(self):
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--window-size=1000,5000')
        self.driver = webdriver.Firefox(options=options)

    def open(self):
        self.driver.get(self.URL)

    def select_lang(self):
        ul_lang = self.driver.find_element(By.CLASS_NAME, 'navbar-nav')
        ul_lang.click()
        a_lang_en = self.driver.find_element(By.ID, 'LinkButton_en')
        a_lang_en.click()

    @property
    def elem_select_districts(self):
        return self.driver.find_element(By.ID, 'ContentMain_ddlADis')

    @property
    def districts_names(self):
        select_districts = self.elem_select_districts
        districts_names = []
        for option in select_districts.find_elements(By.TAG_NAME, 'option'):
            if option.text == '(Select)':
                continue
            districts_names.append(option.text)
        return districts_names

    def select_district(self, district_name):
        select_districts = self.elem_select_districts
        option = select_districts.find_element(
            By.XPATH, f"//option[contains(text(), \"{district_name}\")]"
        )
        option.click()

    @property
    def elem_select_lgs(self):
        return self.driver.find_element(By.ID, 'ContentMain_ddlLGA')

    @property
    def lg_names(self):
        select_lgs = self.elem_select_lgs
        lg_names = []
        for option in select_lgs.find_elements(By.TAG_NAME, 'option'):
            if option.text in ['(Select)', 'lga e 1']:
                continue

            if any(
                [
                    option.text.strip() == '',
                    option.text.startswith('Koralai Pattu West'),
                    option.text.startswith('Seruvila P.S'),
                ]
            ):
                lg_name = '-v' + option.get_attribute("value")
            else:
                lg_name = option.text

            lg_names.append(lg_name)
        return lg_names

    def select_lg(self, lg_name):
        select_lgs = self.elem_select_lgs
        if lg_name.startswith('-v'):
            value = lg_name[2:]
            option = select_lgs.find_elements(
                By.XPATH, f"//option[@value=\"{value}\"]"
            )[
                -1
            ]  # HACK to get around Kurunegala/Kandy BUG
        else:
            option = None
            for cand_option in select_lgs.find_elements(
                By.TAG_NAME, 'option'
            ):
                if clean(cand_option.text) == clean(lg_name):
                    option = cand_option
                    break
            if not option:
                raise Exception(f"lg_name not found: {lg_name}")
        option.click()

    def click_captcha(self):
        while True:
            try:
                iframe_captcha = WebDriverWait(
                    self.driver, self.WAIT_TIME_FOR_DISPLAY_BUTTON_LOAD
                ).until(
                    EC.element_to_be_clickable((By.TAG_NAME, 'iframe')),
                )
                iframe_captcha.click()
                break
            except BaseException:
                self.sleep(2, 3)

    def click_display(self):
        while True:
            try:
                a = WebDriverWait(
                    self.driver, self.WAIT_TIME_FOR_DISPLAY_BUTTON_LOAD
                ).until(
                    EC.element_to_be_clickable(
                        (By.ID, 'ContentMain_cmdDisplay')
                    ),
                )
                a.click()
                break
            except BaseException:
                self.sleep(2, 2)

    @property
    def elem_select_party(self):
        return self.driver.find_element(By.ID, 'ContentMain_ddlPP')

    @property
    def party_names(self):
        select_party = self.elem_select_party
        party_names = []
        for option in select_party.find_elements(By.TAG_NAME, 'option'):
            if option.text == '(Select)':
                continue
            party_names.append(option.text)
        return party_names

    def select_party(self, party_name):
        select_party = self.elem_select_party
        option = select_party.find_element(
            By.XPATH, f"//option[contains(text(), \"{party_name}\")]"
        )
        option.click()

    @property
    def fptp_candidate_list(self):
        table = self.driver.find_element(By.ID, 'ContentMain_GridViewPI')
        trs = table.find_elements(By.TAG_NAME, 'tr')
        fptp_candidate_list = []
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) != 2:
                continue
            ward = tds[0].text
            name = tds[1].text
            if not Candidate.is_name_valid(name):
                continue
            fptp_candidate_list.append(dict(ward=ward, name=name))
        return fptp_candidate_list

    @property
    def pr_candidate_list(self):
        table = self.driver.find_element(By.ID, 'ContentMain_GridViewPII')
        trs = table.find_elements(By.TAG_NAME, 'tr')
        pr_candidate_list = []
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) != 1:
                continue
            name = tds[0].text
            if name[0] == '-':
                continue
            pr_candidate_list.append(dict(name=name))
        return pr_candidate_list

    def click_back(self):
        a = self.driver.find_element(By.ID, 'ContentMain_cmdBack')
        a.click()

    def quit(self):
        self.driver.close()
        self.driver.quit()
