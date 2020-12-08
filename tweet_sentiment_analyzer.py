"""
    Chubakov Chyngyz
"""


from .twitter_streaming.py import TweetToFileListener, load_props
from time import sleep

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tweepy import OAuthHandler
from tweepy import Stream
import pandas as pd
import matplotlib.pyplot as plt
from decouple import config
# from urlextract import URLExtract

import json



def get_tweet_stream(output_file, twitter_credentials):
    """
    This function is given and returns a "stream" to listen to tweets and store them in output_file
    To understand how this function works, check it against the code of twitter_streaming in part00_preclass

    :param output_file: the file where the returned stream will store tweets
    :param twitter_credentials: a dicionary containing the credentials to aceess twitter (you should have created your own!_
    :return: a "stream" variable to track live tweets
    """
    access_token = twitter_credentials['access_token']
    access_token_secret = twitter_credentials['access_token_secret']
    consumer_key = twitter_credentials['consumer_key']
    consumer_secret = twitter_credentials['consumer_secret']

    l = TweetToFileListener()
    l.set_output_file(output_file)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    return stream


def listen_and_store_tweets(keywords, duration, output_file, twitter_credentials):
    """
    This function tracks live tweets on a given topic for a certain duration and stores them in a file

    :param keywords: a list of keywords to track
    :param duration: the time the tracking will stay alive, e.g., 10 seconds
    :param output_file: the file where tweets will be stored
    :param twitter_credentials: a dictionary with credentials to access twitter
    """
    stream = get_tweet_stream(output_file, twitter_credentials)
    print("Beginning listening to tweets for {0} seconds...".format(duration))
    stream.filter(track = keywords, is_async = True)
    sleep(duration)
    stream.disconnect()
    print("...STOP.")

def count_tweets(output_file):
    """
    This function counts the number of tweets stored in output_file
    :returns the number of tweets in output_file
    """
    file = open(output_file, "r")
    count = 0
    for line in file:
        if line is not '\n':
            count += 1
    file.close()
    return count


def listen_and_store_tweets_lan(keywords, duration, lan, output_file, twitter_credentials):
    """
    This function tracks live tweets on a given topic
    and in given languages for a certain duration and stores them in a file

    :param keywords: a list of keywords to track
    :param duration: the time the tracking will stay alive, e.g., 10 seconds
    :param lan: a list of languages to track, e.g. ['en', 'es', 'it'] tracks only tweets in English and Spanish (Espanol) and Italian
    :param output_file: the file where tweets will be stored
    :param twitter_credentials: a dictionary with credentials to access twitter
    """
    stream = get_tweet_stream(output_file, twitter_credentials)
    print("Beginning listening to tweets in {1} for {0} seconds...".format(lan, duration))
    stream.filter(track=keywords, languages = lan, is_async=True)
    sleep(duration)
    stream.disconnect()
    print("...STOP.")




#######  2222222222
# display the text and user info of tweets mae by users with more than follow_num followers
def create_dataframe(output_file):
    """


    :param output_file: the file where tweets are stored
    :return:
    """
    TWEET = []
    file = open(output_file, "r")
    count = 0
    for line in file:

        if line is not '\n':
            try:
                tweet = json.loads(line)
                TWEET.append({
                    'username': tweet['user']['name'],
                    'text' : tweet['text'],
                    'location' : tweet['user']['location'],
                    'lang' : tweet['lang']
                })

            except:
                print("ERROR")
    tweet_json = pd.DataFrame(TWEET, columns=['username', 'text', 'location',
                                                     'lang'])
    file.close()
    return tweet_json



def clean_dataframe(dataframe):

    df1 = dataframe[~dataframe.text.str.contains('https://')]
    df2 = df1[~df1.text.str.contains('RT @')]
    en_df = df2[df2['lang'] == 'en']
    return en_df

#######  33333333
def get_top_lang(df):
    df_top_freq = df.groupby(['lang'])['lang'].agg(
        {"code_count": len}).sort_values(
        "code_count", ascending=False).head(5).reset_index()
    plt.bar(df_top_freq['lang'], df_top_freq['code_count'])
    plt.xlabel('Languages')
    plt.ylabel('Count')
    plt.show()

#######  444444

def get_top_loc(df):
    df_top_freq = df.groupby(['location'])['location'].agg(
        {"code_count": len}).sort_values(
        "code_count", ascending=False).head(5).reset_index()
    plt.bar(df_top_freq['location'], df_top_freq['code_count'])
    plt.xlabel('Locations')
    plt.ylabel('Count')
    plt.show()

    print(df_top_freq)

def get_relevant_word(df, keywor_list):
    text = df['text']
    new_data = []
    for i in text:
        for j in keywor_list:
            if j in i:
                new_data.append(i)
    df = pd.DataFrame(new_data, columns=['text'])

    return df

def get_relevant_sentiment(df):
    text = df['text']
    new_data = []
    for i in text:
        analyser = SentimentIntensityAnalyzer()
        score = analyser.polarity_scores(i)
        rb = score
        lb = score['compound']
        new_data.append(lb)
        print("Text:")
        print(i)
        print("Sentiment scores:")
        print(rb, "\n")
    df['score'] = new_data
    new_df = df[df['score'] < 0]
    print(new_df)
    new_df.to_csv("/Users/chyngyz/Desktop/DSP/SNA/relevant_dataframe.csv", sep=';', encoding='utf-8', index=False, columns=['username', 'text', 'location', 'lang', 'score'])




def prog_lang_count(df, keywor_list):
    text = df['text']
    new_data = []
    for i in text:
        for j in keywor_list:
            if j in i:
                new_data.append({
                    'language' : j
                    }
                )
    df = pd.DataFrame(new_data, columns=['language'])

    df_top_freq = df.groupby(['language'])['language'].agg(
        {"code_count": len}).sort_values(
        "code_count", ascending=False).head(df.size).reset_index()
    print(df_top_freq)
    plt.bar(df_top_freq['language'], df_top_freq['code_count'])
    plt.xlabel('Language')
    plt.ylabel('Count')
    plt.show()
    print(df)

'''def find_links(df, list):

    text = df['text']
    for i in text:
        for j in list:
            if j in i:
                print(j)
                extractor = URLExtract()
                urls = extractor.find_urls(i)
                delete
'''






if __name__ == '__main__':
    access_token, access_token_secret, consumer_key, consumer_secret = load_props("api.txt")

    # Variables that contains the user credentials to access Twitter API
    # Hidden with python decouple
    access_token = config("ACCESS_TOKEN")
    access_token_secret = config("ACCESS_TOKEN_SECRET")
    consumer_key = config("CONSUMER_KEY")
    consumer_secret = config("CONSUMER_SECRET")

    tweet_cred = {'access_token' : access_token,'access_token_secret' : access_token_secret, 'consumer_key' : consumer_key, 'consumer_secret' : consumer_secret }

    """ UNCOMMENT lineby line to text your functions"""

    #### Extracting all tweets to run sentiment analysis on by keyword(Type in desired words)
    listen_and_store_tweets(['love', 'hate'], tweet_cred)


    #### Creating a dataframe
    dataframe = create_dataframe("lang_tweets.json")


    #### Adding english only tweets to dataframe

    cl_dataframe = clean_dataframe(dataframe)
    print(cl_dataframe)


    relevant = get_relevant_sentiment(cl_dataframe)


