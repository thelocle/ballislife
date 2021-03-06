from django.utils.dateparse import parse_datetime
from bs4 import BeautifulSoup as bs
import json, re
from .models import Article
from .config import news_api_key
from .parsehelper import get_page, get_bleacher_report_body_text, get_reporter_name
from .Espn import get_espn_article
from .keywords import keywords
import logging

espn_regex_reporter = "ESPN.+?Writer"

logger = logging.getLogger('ftpuploader')

class NewsApi:
    urls = [
        "https://newsapi.org/v2/everything?sources=bleacher-report&apiKey=", 
        "https://newsapi.org/v2/top-headlines?sources=espn&apiKey=",
        "https://newsapi.org/v2/everything?sources=fox-sports&apiKey="
    ]

    def get_articles(self):
        try:
            for j in self.urls:
                getapi = get_page(f"{j}{news_api_key}").text
                converttojson = json.loads(getapi)['articles']
                for i in range(len(converttojson)):
                    description = converttojson[i]['description']
                    headline = converttojson[i]['title']
                    source = converttojson[i]['source']['name']
                    if any(x in description for x in keywords):
                        url = converttojson[i]['url']
                        print(f'\n**** processing NewsApi  ****\nURL:{url}\n****  **** ****\n')
                        url_image = converttojson[i]['urlToImage']
                        reporter = converttojson[i]['author']
                        if source == "ESPN":
                            reporter = get_reporter_name(reporter, espn_regex_reporter)
                            article_dict = get_espn_article(url)
                            body = article_dict['Body']
                            if reporter is not None:
                                reporter = article_dict['Reporter']
                        elif source == "Bleacher Report":
                            reporter = get_reporter_name(reporter)
                            body = get_bleacher_report_body_text(url)
                        else:
                            body = "None"
                        published_date = parse_datetime(converttojson[i]['publishedAt'])
                        Article.objects.get_new_article(url, url_image, reporter, body, source, description, headline, published_date)
                    else:
                        print(f"Headline:'{headline}'\nSouce: '{source}'\nNot basketball related\n")
                        continue
        except BaseException as e:
            logger.error(f'Failed:{e}')