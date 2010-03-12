import urllib
import simplejson

def getStatus():
    return simplejson.load(urllib.urlopen("http://api.twitter.com/users/show/15527964.json"))['status']['text']

    # The following line is for testing on my localhost, which is in Beijing and therefore Twitter is blocked.
#    return "03-05-2010; 13:00; PM2.5; 88.0; 55; Moderate // Ozone; 43.3; 36; Good"
