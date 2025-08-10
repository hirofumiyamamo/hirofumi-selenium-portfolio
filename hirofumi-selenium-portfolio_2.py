from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# ChromeDriverのパス
CHROMEDRIVER_PATH = r'C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

# テスト対象URL
LOGIN_URL = 'https://the-internet.herokuapp.com/login'
FORM_URL = 'https://the-internet.herokuapp.com/forgot_password'

# スクリーンショット保存ディレクトリ
SCREENSHOT_DIR = 'screenshots'
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def setup_driver():
    options = Options()
    options.add_argument('--headless')  # GUIなしモード
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def save_screenshot(driver, name):
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    driver.save_screenshot(path)
    print(f"Screenshot saved: {path}")

def login_test(driver, username, password):
    driver.get(LOGIN_URL)
    try:
        # 要素が現れるまで最大10秒待機
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
        user_elem = driver.find_element(By.ID, 'username')
        pass_elem = driver.find_element(By.ID, 'password')

        user_elem.clear()
        user_elem.send_keys(username)
        pass_elem.clear()
        pass_elem.send_keys(password)

        # ログインボタンをクリック
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # ページ遷移完了待機（成功/失敗メッセージの有無）
        time.sleep(1)

        page_source = driver.page_source
        if 'You logged into a secure area!' in page_source:
            return True
        elif 'Your username is invalid!' in page_source or 'Your password is invalid!' in page_source:
            return False
        else:
            save_screenshot(driver, f'login_{username}')
            return None

    except Exception as e:
        save_screenshot(driver, f'login_error_{username}')
        print(f"Login test error for user '{username}': {e}")
        return None

def form_test(driver, input_dict):
    driver.get(FORM_URL)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        email_elem = driver.find_element(By.ID, 'email')
        email_elem.clear()
        email_elem.send_keys(input_dict.get('email', ''))

        # フォーム送信ボタン押す
        driver.find_element(By.ID, 'form_submit').click()

        # 送信結果表示まで少し待機
        time.sleep(1)

        page_source = driver.page_source
        if 'Your e-mail\'s been sent!' in page_source:
            return True
        else:
            save_screenshot(driver, f'form_{input_dict}')
            return False

    except Exception as e:
        save_screenshot(driver, f'form_error_{input_dict}')
        print(f"Form test error with input {input_dict}: {e}")
        return False

def main():
    driver = setup_driver()

    login_cases = [
        ('tomsmith', 'SuperSecretPassword!'),   # 正常系ユーザ
        ('tomsmith', 'WrongPassword'),          # 間違ったパスワード
        ('', ''),                               # 未入力
    ]
    form_cases = [
        {'email': 'foo@example.com'},           # 正常系
        {'email': ''},                          # 空メール（境界値テスト）
    ]

    print('--- ログインテスト開始 ---')
    for uname, pwd in login_cases:
        result = login_test(driver, uname, pwd)
        print(f'ログイン結果 [ユーザ:{uname}] → {result}')

    print('--- フォーム送信テスト開始 ---')
    for form_case in form_cases:
        result = form_test(driver, form_case)
        print(f'フォーム送信結果 {form_case} → {result}')

    driver.quit()

if __name__ == '__main__':
    main()