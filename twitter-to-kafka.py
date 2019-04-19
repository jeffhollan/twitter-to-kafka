#!/usr/bin/env python

"""This script uses the Twitter Streaming API, via the tweepy library,
to pull in tweets and publish them to a Kafka topic.
"""

import base64
import datetime
import os
import logging
from backports import configparser
import simplejson as json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from kafka import KafkaProducer

# Get your twitter credentials from the environment variables.
# These are set in the 'twitter-stream.json' manifest file.

config = configparser.RawConfigParser()
config.read('config.cfg')

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
TWITTER_STREAMING_MODE = os.environ.get('TWITTER_STREAMING_MODE')
KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
SEARCH_TERM = os.environ.get('SEARCH_TERM')
NUM_RETRIES = 3

class StdOutListener(StreamListener):
    """A listener handles tweets that are received from the stream.
    This listener dumps the tweets into a Kafka topic
    """
    
    producer = KafkaProducer(bootstrap_servers=KAFKA_ENDPOINT)

    def on_data(self, data):
        """What to do when tweet data is received."""
        data_json = json.loads(data)
        self.producer.send(KAFKA_TOPIC, json.dumps(data_json).encode('utf-8'))
        print(json.dumps(data_json))

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
        )

    listener = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    print('stream mode is: %s' % TWITTER_STREAMING_MODE)

    stream = Stream(auth, listener)
    # set up the streaming depending upon whether our mode is 'sample', which
    # will sample the twitter public stream. If not 'sample', instead track
    # the given set of keywords.
    # This environment var is set in the 'twitter-stream.yaml' file.
    if TWITTER_STREAMING_MODE == 'sample':
        stream.sample()
    else:
        stream.filter(track=[SEARCH_TERM])