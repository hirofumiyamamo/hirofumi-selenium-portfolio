from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Chromeドライバーのパス (ローカル環境に合わせて変更してください)
CHROMEDRIVER_PATH = r'C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'


# 検索キーワード
SEARCH_KEYWORD = 'ノートパソコン'

# CSV出力ファイル名
CSV_FILE = 'amazon_products.csv'

def setup_driver():
    options = Options()
    options.add_argument('--headless')  # ブラウザを非表示にする場合
    options.add_argument('--disable-gpu')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_product_info(driver):
    product_list = []

    # ページ内商品の要素を待機して取得
    products = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot div.s-result-item'))
    )

    for product in products:
        try:
            title = product.find_element(By.CSS_SELECTOR, 'h2 a span').text
        except:
            title = ''

        try:
            price_whole = product.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
            price_fraction = product.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text
            price = price_whole + price_fraction
        except:
            price = ''

        try:
            review_count = product.find_element(By.CSS_SELECTOR, 'span.a-size-base').text
        except:
            review_count = ''

        if title:  # タイトルがない商品はスキップ
            product_list.append({
                '商品名': title,
                '価格': price,
                'レビュー数': review_count
            })
    return product_list

def main():
    driver = setup_driver()
    driver.get('https://www.amazon.co.jp')

    # 検索ボックスにキーワードを入力し検索
    search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    search_box.send_keys(SEARCH_KEYWORD)
    search_box.send_keys(Keys.RETURN)

    all_products = []

    for page in range(1, 4):  # 3ページ分クロール（必要に応じて調整可能）
        time.sleep(3)  # ページ読み込み待ち（適宜調整）
        products = get_product_info(driver)
        all_products.extend(products)

        # 「次へ」ボタンをクリックして次ページへ
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'ul.a-pagination li.a-last a')
            next_button.click()
        except:
            print('次のページが見つかりません。終了します。')
            break

    # CSVに書き込み
    keys = ['商品名', '価格', 'レビュー数']
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_products)

    print(f'{len(all_products)} 件の商品情報を {CSV_FILE} に保存しました。')
    driver.quit()

if __name__ == '__main__':
    main()
