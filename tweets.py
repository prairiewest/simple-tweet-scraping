#!/usr/local/bin/python3

#
# Simple client for querying the Twitter public API
#
# Twitter auth is in the config.txt file; it should look like this:
#{
#	"ACCESS_TOKEN":    "get_this_from_twitter_applications_page",
#	"ACCESS_SECRET":   "get_this_from_twitter_applications_page",
#	"CONSUMER_KEY":    "get_this_from_twitter_applications_page",
#	"CONSUMER_SECRET": "get_this_from_twitter_applications_page",
#	"max_tweets":      5000
#}
#

import sys
import json
from datetime import datetime

# Import the necessary methods from "twitter" library
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

if sys.version_info[0] < 3:
    raise Exception("Python 3 is required to run this script")

try:
	with open('config_json.txt') as config_file:    
    	config = json.load(config_file)
except Exception as e:
	print("Could not load configuration from config_json.txt")
	exit

oauth = OAuth(config['ACCESS_TOKEN'], config['ACCESS_SECRET'], config['CONSUMER_KEY'], config['CONSUMER_SECRET'])

# Initiate the connection to Twitter
twitter_search = Twitter(auth=oauth)

query_terms = ["Testing"]
if len(sys.argv) > 1:
	query_terms = sys.argv[1:]

# This is the data we want to pull from each tweet
data_headers = ["id","user","created_at","text","truncated","lang","geo","coordinates","place","retweet_count","favorite_count"]

# Save each new file with a date and time stamp
datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H%M')
filename = '{}_tweets.csv'.format(datestring)

def get_max_id(r):
	if "next_results" in r["search_metadata"]:
		string1 = r["search_metadata"]["next_results"].split("&")
		string2 = string1[0].split("?max_id=")
		max_id = string2[1]
		return max_id
	return None

def has_more_results(r):
	if "search_metadata" in r:
		if "next_results" in r["search_metadata"]:
			return True
	return False 

with open(filename, 'w') as f:
	# Write the header row
	f.write('"{0}"'.format('","'.join(data_headers)))
	f.write(',"location_unreliable","url"') #Add calculated columns
	f.write("\n")

	for query in query_terms:
		search_more = True
		max_id = None
		count = 0

		while search_more:
			# Send a query to the search interface
			results = twitter_search.search.tweets(q=query, lang='en', count=1000, max_id=max_id)
			search_more = has_more_results(results)
			max_id = get_max_id(results)

			count = count + len(results['statuses'])
			if count > config['max_tweets']:
				search_more = False

			# Print each tweet as a new row 
			for tweet in results['statuses']:
				line = []
				user_location = ""
				location_from_user = False
				for h in data_headers:

					if isinstance(tweet[h], str):
						# Strings get linefeeds stripped and then dumped straight out
						line.append('"' + tweet[h].replace('\r', '').replace('"', '""') + '"')

					elif isinstance(tweet[h], dict):
						# Dictionaries need to be handled individually
						if (h=="user"):
							if ("screen_name" in tweet[h]):
								line.append('"' + tweet[h]['screen_name'] + '"')
							else:
								line.append(json.dumps(tweet[h]))
							if ("location" in tweet[h]):
								user_location = str(tweet[h]['location'])
						elif (h=="place"):
							if ("full_name" in tweet[h] and tweet[h]['full_name'] != None):
								line.append('"' + tweet[h]['full_name'] + '"')
							elif ("name" in tweet[h] and tweet[h]['name'] != None):
								line.append('"' + tweet[h]['full_name'] + '"')
							else:
								line.append('"' + user_location + '"')
								location_from_user = True
						elif (h=="coordinates"):
							if ("coordinates" in tweet[h] and isinstance(tweet[h]['coordinates'], list)):
								line.append('"' + ",".join(map(str,tweet[h]['coordinates'])) + '"')
							else:
								line.append(json.dumps(tweet[h]))
						elif (h=="geo"):
							if ("coordinates" in tweet[h] and isinstance(tweet[h]['coordinates'], list)):
								line.append('"' + ",".join(map(str,tweet[h]['coordinates'])) + '"')
							else:
								line.append(json.dumps(tweet[h]))
						else:
							line.append(json.dumps(tweet[h]))

					elif isinstance(tweet[h], float):
						line.append('"' + str(tweet[h]) + '"')

					elif isinstance(tweet[h], int):
						if (h=="id"):
							line.append('"""' + str(tweet[h]) + '"""')
						else:
							line.append('"' + str(tweet[h]) + '"')

					else:
						# Default action should mean None type, but use JSON dumps() in case we missed something
						if (h=="place"):
							# If we get here it means that the tweet location is None, so we will copy the user-supplied location string
							line.append('"' + user_location + '"')
							location_from_user = True
						else:
							line.append(json.dumps(tweet[h]))
				f.write('{0}'.format(','.join(line)))
				f.write(',"' + str(location_from_user) + '"')
				f.write(',"' + "https://twitter.com/" + tweet["user"]["screen_name"] + "/status/" + str(tweet["id"]) + '"' )
				f.write("\n")

		print("Got %i tweets for %s" % (count, query))

# End of script
