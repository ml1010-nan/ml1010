#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 19:12:11 2018

@author: silviu
"""

from __future__ import print_function
from __future__ import unicode_literals

from pattern.db import Datasheet, pprint, pd
from pattern.en import sentiment, polarity, subjectivity, positive

import requests
from bs4 import BeautifulSoup

counter = 0

'''Package what we did above into a function'''
def scrape_news_text(news_url):
    
    global counter
 
    news_html = requests.get(news_url).content
    
#    print(news_html)
 
    '''convert html to BeautifulSoup object'''
    news_soup = BeautifulSoup(news_html , 'lxml')
# soup.find("div", {"id": "articlebody"})
#    paragraphs = [par.text for par in news_soup.find_all('p')]
#    news_text = '\n'.join(paragraphs)

#    print(news_soup.find("div", {"id": "articleText"}))
    
    
    date_object = news_soup.find(itemprop="datePublished")
    news_object = news_soup.find("div", {"id": "articleText"})
    
    if date_object is None:
        return "  "
    
    if news_object is None:
        return "   "


    news_date = date_object.get_text()#   find("div", {"id": "articleText"}).text
    news_text = news_object.text
    
#    print(news_date)
#    print(news_text)
    print(news_url)
    
    try:
        # We'll store tweets in a Datasheet.
        # A Datasheet is a table of rows and columns that can be exported as a CSV-file.
        # In the first column, we'll store a unique id for each tweet.
        # We only want to add the latest tweets, i.e., those we haven't seen yet.
        # With an index on the first column we can quickly check if an id already exists.
        # The pd() function returns the parent directory of this script + any given path.
        table = Datasheet.load(pd("nasdaq2.csv"))
    except:
        table = Datasheet()
        
    news_sentiment = sentiment(news_text)
    
    print(news_sentiment)
        
    table.append([counter, news_date, news_url, news_sentiment])

    table.save(pd("nasdaq2.csv"))    
    
    counter += 1

    return news_text 

'''Generalized function to get all news-related articles from a Nasdaq webpage'''
def get_news_urls(links_site):
    '''scrape the html of the site'''
    resp = requests.get(links_site)
 
    if not resp.ok:
        return None
 
    html = resp.content
 
    '''convert html to BeautifulSoup object'''
    soup = BeautifulSoup(html , 'lxml')
 
    '''get list of all links on webpage'''
    links = soup.find_all('a')
    
    urls = [link.get('href') for link in links]
    urls = [url for url in urls if url is not None]
 
    '''Filter the list of urls to just the news articles'''
    news_urls = [url for url in urls if '/article/' in url]

#    print(news_urls[0])
    
    return news_urls#scrape_news_text(news_urls[0])

def scrape_all_articles(ticker , upper_page_limit = 5):
 
    landing_site = 'http://www.nasdaq.com/symbol/' + ticker + '/news-headlines'
    
#    print(landing_site)
    
#    return get_news_urls(landing_site)
 
    all_news_urls = get_news_urls(landing_site)
 
    current_urls_list = all_news_urls.copy()
 
    index = 2
 
    '''Loop through each sequential page, scraping the links from each'''
    while (current_urls_list is not None) and (current_urls_list != []) and \
        (index <= upper_page_limit):
 
        '''Construct URL for page in loop based off index'''
        current_site = landing_site + '?page=' + str(index)
        
        print(current_site)
        
        current_urls_list = get_news_urls(current_site)
 
        '''Append current webpage's list of urls to all_news_urls'''
        all_news_urls = all_news_urls + current_urls_list
 
        index = index + 1
 
    all_news_urls = list(set(all_news_urls))
 
    '''Now, we have a list of urls, we need to actually scrape the text'''
    all_articles = [scrape_news_text(news_url) for news_url in all_news_urls]
 
    return all_articles


aapl_articles = scrape_all_articles('aapl' , 500)
 
print("Done")

#print(aapl_articles[1])

#print(aapl_articles[2])