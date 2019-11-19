# simple-tweet-scraping
Very simple python script that queries the Twitter API

Make sure you install the twitter module:

```
pip3 install twitter --user
```

You will need to obtain Twitter API tokens (there are 4 tokens you will need in total).  Start here:
https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens

Once you have the tokens, save them in the file "config_json.txt"

You can call the script with multiple keywords or hashtags at once, and it will query them all.  Like this:

```
python3 tweets.py "Test Thing" "#TestThing" "#TThing" TestThing
```

And it will tell you how many tweets it got for each term:

```
Got 77 tweets for Test Thing
Got 5 tweets for #TestThing
Got 0 tweets for #TThing
Got 179 tweets for TestThing
```

If you get an error like this, then you do not have the twitter auth information set up correctly:

```
urllib.error.HTTPError: HTTP Error 401: Authorization Required
```

Regarding geolocation data in tweets: if there was no geolocation data at all then it will copy whatever the user had put down for their own location, however this data is unreliable.  A column is added to indicate that.  Many tweets don't have any location data at all, and that's because people don't generally enable geotagging for all of their tweets (it's off by default – read more https://help.twitter.com/en/safety-and-security/tweet-location-settings ).  The tweets that are geotagged may have been generated by 3rd party apps like 4Square, or sometimes people or apps will turn on geotagging just for photos.

The limit to the amount of tweets that the script will pull per term is in the config file, but 1500 is generally what you're going to be limited to every 15 minutes, as a standard API user.

Here is the page talking about Twitter premium APIs if the standard one isn't enough:
https://blog.twitter.com/developer/en_us/topics/tools/2017/introducing-twitter-premium-apis.html

And here is the page that talks about the differences:
https://developer.twitter.com/en/docs/tweets/search/overview

So if you stick with the free API, you will only ever be able to grab the last 7 days of tweets.  I've added the ID column so that you can de-duplicate the data as needed.
