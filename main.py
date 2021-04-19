import pyautogui
import time
import argparse
import logging

from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

pyautogui.FAILSAFE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLOSE_NOTIFICATION = (413, 83)

FAILURE_TEST_INTERVAL = timedelta(minutes=5)


def goto_class(driver):
    driver.find_element_by_id('btn_guest').click()


def close_chrome_notification():
    pyautogui.click(*CLOSE_NOTIFICATION)


def force_refresh(driver):
    driver.execute_script('window.onbeforeunload = function() {};')
    driver.refresh()


def try_s(func):
    for retry_number in range(10):
        try:
            func()
            break
        except Exception as e:
            logger.exception(e)


def get_vc(driver, args):
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(args.url)


def login(driver, i, usernames):
    force_refresh(driver)
    goto_class(driver)
    if i == 0:
        driver.find_element_by_xpath("//input[@class='full-width']")
        driver.execute_script(
            "document.querySelector('.dlg-nickname .full-width').value"
            f" = '{usernames[i].strip()}';")
        driver.execute_script("document.querySelector('.dlg-nickname .btn').click();")
    else:
        driver.find_element_by_id("app_menu").click()
        driver.find_element_by_xpath("//*[contains(text(), 'اطلاعات کاربری')]").click()
        driver.find_element_by_xpath('//*[@title="ویرایش نام نمایشی"]').click()
        input1 = driver.find_element_by_xpath("//input[@class='box-shrink']")
        input1.clear()
        input1.send_keys(usernames[i].strip())
        driver.find_element_by_xpath('//*[@type="submit"]').click()
        driver.find_element_by_xpath('//*[@class="box-shrink close-button-container"]').click()


def exit_from_vc(driver):
    driver.switch_to.window(driver.window_handles[-1])
    driver.find_element_by_id("app_menu").click()
    driver.find_element_by_xpath("//*[contains(text(), 'خروج')]").click()
    driver.close()


def main():
    parser = argparse.ArgumentParser(description='This command will record a VClass page')
    parser.add_argument('-u', '--url', type=str, default='', help='URL of vclass')
    parser.add_argument('-d', '--duration', type=float, default=0, help='Duration of class in minutes')
    parser.add_argument('-a', '--username', type=str, default='./usernames.txt', help='file Username of skyroom user')
    args = parser.parse_args()
    f = open(args.username, 'r', encoding="utf-8")
    usernames = f.readlines()
    n = len(usernames)
    if args.url != '':
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        logger.info('Opening google chrome')
        driver = None
        for retry_number in range(10):
            try:
                if driver:
                    logger.info('Driver is not none, close it.')
                    driver.close()
                driver = webdriver.Chrome(options=chrome_options)
                driver.implicitly_wait(10)
                driver.maximize_window()
                break
            except Exception as e:
                logger.exception(e)
        for i in range(n):
            if i != 0:
                try_s(lambda: driver.execute_script(f"window.open('about:blank', 'tab_{i}');"))
            logger.info(f'Open vc for tab {i + 1}')
            try_s(lambda: get_vc(driver, args))
            logger.info(f'Login as guest for {i+1}')
            try_s(lambda: login(driver, i, usernames))
            close_chrome_notification()

        time.sleep(60 * args.duration)
        for i in range(n):
            logger.info(f"exit tab{i + 1}")
            try_s(lambda: exit_from_vc(driver))


if __name__ == "__main__":
    main()
