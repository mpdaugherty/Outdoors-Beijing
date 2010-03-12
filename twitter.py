import urllib
import simplejson

def getRecentStatuses():
    statuses = simplejson.load(urllib.urlopen("http://api.twitter.com/1/statuses/user_timeline/beijingair.json?count=2"))
    cleanStatuses = []
    for status in statuses:
        cleanStatuses.append(status['text'])
    return cleanStatuses

    # The following line is for testing on my localhost, which is in Beijing and therefore Twitter is blocked.
#    return "03-05-2010; 13:00; PM2.5; 88.0; 55; Moderate // Ozone; 43.3; 36; Good"
