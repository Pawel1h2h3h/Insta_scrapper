from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.instagram.com/paweljaa/"


headers = {

   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

}

response = requests.get(url, headers=headers)


class Post:
    def __init__(self, url, comments=None) -> None:
        self.url = url
        self.comments = comments if comments else []

    def open_post(self):
        link = self.url
        self.driver = webdriver.Chrome()
        self.driver.get(link)

        self.accept_cookies()
        self.log_in()

        time.sleep(5)
        self.driver.get(link)
        time.sleep(2)

    def accept_cookies(self):
        cookie_button = self.driver.find_element(By.XPATH, "//button[text()='Zezwól na wszystkie pliki cookie']")
        cookie_button.click()

    def log_in(self, username="", password=""):
        wait = WebDriverWait(self.driver, 10)
        start_log = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[text()='Zaloguj się']")))
        self.driver.execute_script("arguments[0].click();", start_log)

        username_field, password_field = self.find_fields()
        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = self.driver.find_element(By.XPATH, "//div[text()='Zaloguj się']")
        login_button.click()

    def find_fields(self):
        wait = WebDriverWait(self.driver, 15)
        username_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Numer telefonu, nazwa użytkownika lub adres e-mail']")))

        wait = WebDriverWait(self.driver, 10)
        password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@aria-label='Hasło']")))

        return username_field, password_field

    def get_comment(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.x1lliihq.x1plvlek.xryxfnj")))
        return element.text

    def get_comments(self, wait_time=100):
        """
        Funkcja wydobywa treści komentarzy z postu na Instagramie.
        """
        try:
            comments_section = dupa(self.driver)
        except TimeoutError as e:
            print(e)

        # wait = WebDriverWait(self.driver, wait_time)
        # comments_section = wait.until(EC.presence_of_all_elements_located(
        #     (By.CSS_SELECTOR, "span.x1lliihq.x1plvlek.xryxfnj")
        # ))

        # Wyodrębnienie tylko tekstów komentarzy
        comments = []
        for comment in comments_section:
            try:
                body = comment.text.strip()  # Pobranie czystego tekstu
                if body:  # Pomijanie pustych tekstów
                    comments.append(body)
            except Exception as e:
                print(f"Błąd przy przetwarzaniu komentarza: {e}")

        self.comments = comments
        return comments

    def load_more_comments(self):
        # scrollable_element = self.driver.find_element(By.CSS_SELECTOR, "div.x5yr21d.xw2csxc.x1n2onr6")
        scrollable_element = self.driver.find_element(By.CSS_SELECTOR, "div.x5yr21d.xw2csxc.x1odjw0f.x1n2onr6")
        # Przewijanie pola za pomocą JavaScript
        # for _ in range(10):  # Liczba iteracji odpowiada liczbie przewinięć
        #     self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", scrollable_element)
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
        while True:
            # Przewiń w dół
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
            time.sleep(3)  # Poczekaj na załadowanie nowych danych
            # Sprawdź, czy przewijanie się zakończyło
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
            if new_height == last_height:
                time.sleep(2)
                break
            last_height = new_height

    def quit(self):
        self.driver.quit()


class DataBase:
    def __init__(self, comments) -> None:
        self.comments = comments

    def write_comments_to_file(self, path):
        with open(path, 'w') as fp:
            for comment in self.comments:
                fp.write(f'{comment}\n')


def dupa(driver):
    # iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    # driver.switch_to.frame(iframe)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.x1lliihq")))
    return element

post = Post('https://www.instagram.com/reel/DAWKc3DoQ8J/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==')
post.open_post()
post.load_more_comments()
c = post.get_comments()

data = DataBase(c)
data.write_comments_to_file('comments.txt')
post.quit()