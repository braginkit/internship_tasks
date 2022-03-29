import requests
from bs4 import BeautifulSoup as bs
import re


def last_article(url):
    rs = requests.get(url)
    root = bs(rs.content, 'html.parser')
    root.prettify()
    article = root.select('.content-container', limit=1)
    article = str(article)
    article = article[1:-1]
    article = re.sub('<[^>]+>', '', article)
    article = re.sub('  ', '', article)
    split_article = article.split("Статьи редакции", 1)
    massage = split_article[0]
    massage = re.sub(' Статьи редакции', '', massage)
    massage = re.sub('\n', '', massage)
    massage += '\nИсточник: vc.ru'

    return massage


url = 'https://vc.ru/new'
text = last_article(url)
print(text)