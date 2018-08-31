'''
Author: B. Aditya, aditya.bulusu168@gmail.com
Title: Twitter Sentiment Analysis
Description: The following code corresponds to sentiment analysis of tweets to classify them into positive, negative
             or neutral and generate results in the form of bar charts, word clouds and tables. The classification is done
             on the basis of the polarity of the tweet with reference to a huge corpus. Tweets with positive polarity are
             classified as positive, and te same applies to negative as well as the neutral tweets. Dig deep into the code to
             understand the implementation. Tweets are obtained in windows of 100 ( for whatever the number of tweets
             are to be analyzed ).
Modules: tweepy, textblob, plotly, wordcloud
'''
# All the necessary imports
from tweepy import OAuthHandler, API, Cursor
from os import environ
from textblob import TextBlob
from re import sub
import matplotlib.pyplot as pplot
from wordcloud import WordCloud
from plotly.offline import plot
import plotly.graph_objs as go

# Utility function for cleaning tweets
def clean_tweet(tweet):
    cleaned_tweet = sub(r'@\w+|https://\w+|www.\w+', '', tweet)  # Remove Hyperlinks and references
    cleaned_tweet = sub(r'\W+', ' ', cleaned_tweet)  # Remove unnecessary characters
    cleaned_tweet = sub(r'#', '', cleaned_tweet)  # Remove hash tags
    cleaned_tweet = sub(r'RT', '', cleaned_tweet)  # Remove the re-tweets
    return cleaned_tweet

# Utility function to create an API from the credentials (stored as environment variables)
def setup_twitter():
    api = None
    try:
        consumer_key = environ['TWITTER_API_KEY']
        consumer_secret_token = environ['TWITTER_API_SECRET_KEY']
        access_token = environ['TWITTER_ACCESS_TOKEN']
        access_secret_token = environ['TWITTER_ACCESS_SECRET_TOKEN']
        print('Connecting to twitter...')
        auth_handle = OAuthHandler(consumer_key, consumer_secret_token)  # Authenticating the user to get a handler
        auth_handle.set_access_token(access_token, access_secret_token)  # Setting the access tokens for the api
        api = API(auth_handle, wait_on_rate_limit=True)  # Getting an API for the handler
        print('Connected! Analyzing tweets... (this might take time based on the number of tweets)')
    except Exception as e:
        print("Error occurred! Message: ",e)
    return api

# Utility function to evaluate the polarities and generate sentiments
def get_tweets_and_sentiment(hashtags=None, number_of_tweets=1000):
    api = setup_twitter()
    if api is None:
        return "Twitter setup failed! Please check your credentials!"
    results = {'positive': [], 'negative': [], 'neutral': []}  # Results dictionary that holds results for all the hash tags
    for hashtag in hashtags:
        print('Analysis for', hashtag, 'started.')
        positive_tweets = 0
        negative_tweets = 0
        neutral_tweets = 0
        analyzed_tweets = 0
        last_window = number_of_tweets % 100  # Calculating the last window for the given number of tweets
        text = []
        while analyzed_tweets < number_of_tweets :
            count_per_request = 100
            if (number_of_tweets - analyzed_tweets) == last_window:
                count_per_request = last_window
            for tweet in Cursor(api.search, q=hashtag, lang='en').items(count_per_request):  # Obtaining 100 tweets at a time
                try:
                    cleaned_tweet = clean_tweet(str(tweet.text))  # Pre-processing the tweet
                    text.append(cleaned_tweet)  # List for generating word cloud
                    cleaned_tweet = TextBlob(cleaned_tweet)  # Getting a TextBlob object for the tweet to calculate the polarity
                    for sentence in cleaned_tweet.sentences:
                        polarity = sentence.sentiment.polarity  # Finding polarity of the sentence for classifying it
                        if polarity > 0.0 :
                            positive_tweets += 1
                        elif polarity < 0.0 :
                            negative_tweets += 1
                        else:
                            neutral_tweets += 1
                    analyzed_tweets += 1
                except Exception:
                    continue
            print(str(analyzed_tweets), " tweets analyzed for", hashtag, " Remaining tweets: ", str(number_of_tweets - analyzed_tweets))
        print("Analysis for ", hashtag, "completed.")
        word_cloud = WordCloud().generate_from_text(' '.join(text))  # Generate a word cloud for a hash tag
        pplot.imsave(arr=word_cloud, fname='Word_Cloud_'+hashtag+'.png', format='png')
        print('Word Cloud for', hashtag, 'generated successfully as Word_Cloud_'+hashtag)
        results['positive'].append(positive_tweets)
        results['negative'].append(negative_tweets)
        results['neutral'].append(neutral_tweets)
    return results

# Main function to accept input and obtain bar chart and table for the result
if __name__ == '__main__':
    try:
        hashtags_set = input('Enter Hashtags (separate by comma\',\' for multiple hashtags) : ')
        hashtags = sub(r'\W&^,', '', hashtags_set)
        hashtags = hashtags.split(',')
        hashtags = [''.join(['#', hashtag]) for hashtag in hashtags]  # Getting a list of hash tags from the user
        hash_set = hashtags_set.replace(',', '_')
        number_of_tweets = int(input('Enter maximum number of tweets (minimum 1000 suggested) : '))
        results = get_tweets_and_sentiment(hashtags, number_of_tweets)
        print("Please wait while we generate the bar plot and table for the results...")
        positive_data_bar = go.Bar(x=hashtags, y=results['positive'], name='Positive')  # Generate a positive data bar for the positive results
        negative_data_bar = go.Bar(x=hashtags, y=results['negative'], name='Negative')  # Generate a negative data bar for the negative results
        neutral_data_bar = go.Bar(x=hashtags, y=results['neutral'], name='Neutral')  # Generate a neutral data bar for the neutral results
        plot({  # Grouping all the results into a single bar chart
            "data": [positive_data_bar, negative_data_bar, neutral_data_bar],
            "layout": go.Layout(barmode='group', title="Bar Plot for Tweet Analysis of Hashtags " + hashtags_set),
        }, auto_open=True, image='png', image_filename="Bar_Plot_" + hash_set, filename="Bar_Plot_" + hash_set+ '.html')
        plot({  # Generating table for the results
            "data": [go.Table(
                header=dict(
                    values=['Hash Tag', 'Positive', 'Negative', 'Neutral'],
                    fill=dict(color='#C2D4FF'),
                    align=['left'] * 5
                ),
                cells=dict(
                    values=[hashtags, results['positive'], results['negative'], results['neutral']],
                    fill=dict(color='#F5F8FF'),
                    align=['left'] * 5
                )
            )]
        }, auto_open=True, image='png', image_filename='Table_' + hash_set, filename='Table_' + hash_set + '.html')
        print('Bar plot successfully generated and saved as', 'Bar_Plot_' + hash_set + '.html')
        print('Table representation generated and saved as', 'Table_' + hash_set + '.html')
    except Exception as e:
        print('Error occurred! Message: ', e)
