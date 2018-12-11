#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 11:55:18 2018

@author: silviu
"""

from __future__ import print_function
from __future__ import unicode_literals

from builtins import str, bytes, dict, int
from builtins import range

import sys, termios, tty, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pattern.web import Twitter, hashtags
from pattern.db import Datasheet, pprint, pd
from pattern.en import sentiment, polarity, subjectivity, positive



try:
    # We'll store tweets in a Datasheet.
    # A Datasheet is a table of rows and columns that can be exported as a CSV-file.
    # In the first column, we'll store a unique id for each tweet.
    # We only want to add the latest tweets, i.e., those we haven't seen yet.
    # With an index on the first column we can quickly check if an id already exists.
    # The pd() function returns the parent directory of this script + any given path.
    table = Datasheet.load(pd("tweets.csv"))
    index = set(table.columns[0])
except:
    table = Datasheet()
    index = set()

engine = Twitter(language="en")

prev = '1071765537749917696'

counter = 0

while counter < 1000:

    counter += 1
    time.sleep(60)
    for tweet in engine.search("#Apple", start=prev, count=10, cached=False):
        print(tweet.id)
#        print(tweet.text)
#        print(tweet.date)
        tweet_sentiment = sentiment(tweet.text)
        print(tweet_sentiment)
        
        if len(table) == 0 or tweet.id not in index:
             
            table.append([tweet.id, tweet.date, tweet.text, tweet_sentiment])
            index.add(tweet.id)
            
        prev = tweet.id
        
        
        
table.save(pd("tweets2.csv"))