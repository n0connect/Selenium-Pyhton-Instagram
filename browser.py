from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import user_account
import foundGender


class Browser:
    def __init__(self, link):
        self.link = link
        self.driver = webdriver.Firefox()
        Browser.go_instagram_page(self)

    def go_instagram_page(self):
        self.driver.get(self.link)
        print("Opening instagram page...")
        time.sleep(5)
        Browser.login_instagram(self)

    def login_instagram(self):  # Login and go the account page
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        print("Found username_field")
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        print("Found password_field")
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[3]'))
        )
        print("Found login_button")
        username_field.send_keys(user_account.User.user_name)
        print("Sent user_name")
        password_field.send_keys(user_account.User.user_password)
        print("Sent user_password")
        login_button.click()
        print("Click the login button")
        time.sleep(5)
        self.driver.get(user_account.User.account_link)
        print("Opening account_link")
        time.sleep(15)
        print("scroll_down function is start")
        Browser.scroll_down(self)
        print("scroll_down function is stop")

    def scroll_down(self):
        # You can change document.querySelector value
        js_command = """
        page = document.querySelector("._aano");
        page.scrollTo(0,page.scrollHeight);
        var end_page = page.scrollHeight;
        return end_page;
        """
        end_page = self.driver.execute_script(js_command)
        while True:
            end = end_page
            time.sleep(2)
            end_page = self.driver.execute_script(js_command)
            print(f"scrolling... | end: {end} --> end_page: {end_page}")
            if end == end_page:
                check: bool = True
                time.sleep(5)
                for i in range(0, 4):
                    end = end_page
                    time.sleep(2)
                    end_page = self.driver.execute_script(js_command)
                    print(f"scrolling... | end: {end} --> end_page: {end_page}")
                    if end == end_page:
                        check = False
                        Browser.add_followers_in_list(self)
                        break
                if check:
                    break

    def add_followers_in_list(self):
        # You can change value
        followers_list: list = self.driver.find_elements(By.CSS_SELECTOR, '._ap3a._aaco._aacw._aacx._aad7._qqqq')
        count = 1
        try:
            with open(f'followers_output.txt', 'w') as file:
                for follower in followers_list:
                    file.write(f'{count} ---> {follower.text} \n')
                    count += 1
            print("Job is done.")
            self.driver.quit()
            print("Gender API is starting...")
            time.sleep(3)
            foundGender.user_file_path()
        except Exception as ex:
            raise print(f'File operation error: {ex}')

