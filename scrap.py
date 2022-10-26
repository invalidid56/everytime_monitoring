# Junseo Kang, invalidid56@snu.ac.kr
# Scrap texts from Everytime (Univ. Community)
# scrap.py
import configparser
import os.path
import sys
import time
import pandas as pd
from selenium import webdriver


config = configparser.ConfigParser()
config.read('config.ini')

webdriver_options = webdriver.ChromeOptions()
webdriver_options.add_argument('--headless')
webdriver_options.add_argument('--no-sandbox')
webdriver_options.add_argument('--disable-dev-shm-usage')
webdriver_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                               'like Gecko) Chrome/97.0.4692.71 Safari/537.36')


def main(database_file):
    # Check Time
    tm = time.localtime(time.time())
    scraping_time = str(tm.tm_mon).zfill(2) + str(tm.tm_mday).zfill(2) + str(tm.tm_hour).zfill(2)
    # Set Driver Config
    driver = webdriver.Chrome(config['SCRAP']['Driver'], options=webdriver_options)
    driver.implicitly_wait(1)

    # Login
    driver.get('https://everytime.kr/login')
    driver.find_element(by='name', value='userid').send_keys(config['SCRAP']['ID'])
    driver.find_element(by='name', value='password').send_keys(config['SCRAP']['PW'])
    driver.find_element(by='xpath', value='//*[@class="submit"]/input').click()
    driver.implicitly_wait(1)

    # set temps and constants
    results = []
    pages_to_read = 1
    keywords = config['SCRAP']['Keywords'].split(',')

    for keyword in keywords:
        for page in range(pages_to_read):
            driver.get('https://everytime.kr/search/all/{0}/p/{1}'.format(
                keyword,
                page+1
            ))
            driver.implicitly_wait(1)

            # get articles link
            posts = driver.find_elements(by='css selector',
                                        value='article > a.article')
            links = [post.get_attribute('href') for post in posts]

            # get details
            for link in links:
                driver.get(link)
                # get text
                comments = driver.find_elements(by='css selector',
                                               value='p.large')
                for i, comment in enumerate(comments):
                    if i == 0:
                        comment_type = 'article'
                    else:
                        comment_type = 'comment'
                    results.append(
                        {
                            'time': scraping_time,
                            'keyword': keyword,
                            'content': comment.text,
                            'comment_type': comment_type,
                            'url': link
                        }
                    )

        # Convert to Dataframe
        result_df = pd.DataFrame(results)

    # Check Duplication
    if os.path.exists(database_file):
        previous_df = pd.read_csv(database_file)
        result_df = pd.concat([previous_df, result_df])
        result_df = result_df.drop_duplicates(['keyword', 'content'])

    result_df.to_csv(database_file, index=False)


if __name__ == '__main__':
    main(database_file=sys.argv[1])