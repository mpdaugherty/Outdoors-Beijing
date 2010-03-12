import cgi, urllib, os, datetime, logging
import simplejson

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

import twitter

class PollutantStatus(db.Model):
    type = db.StringProperty(required=True)
    date = db.DateTimeProperty(required=True)
    description = db.StringProperty(required=True)
    concentration = db.FloatProperty(required=True)
    aqi = db.IntegerProperty(required=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("<html>")
        self.response.out.write("<head><title>Beijing Air Status</title>");
        self.response.out.write('<link rel="stylesheet" href="stylesheets/main.css" type="text/css" />');
        self.response.out.write("<script src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js\" type=\"text/javascript\"></script>");
        self.response.out.write("<script src=\"js/main.js\" type=\"text/javascript\"></script>");
        self.response.out.write("</head>")

        self.response.out.write("<body>")
        self.response.out.write('<div id="PageContainer">')
        self.response.out.write("<h1>Beijing Air Status</h1>")
        self.response.out.write(self.getCurrentPollutantHTML("PM2.5"))
        self.response.out.write(self.getCurrentPollutantHTML("Ozone"))
        self.response.out.write('</div>')
        self.response.out.write("</body></html>")

    def getCurrentPollutantHTML(self, pollutant):
        pm2Query = PollutantStatus.all()
        pm2Query.order("-date")
        pm2Query.filter("type = ", pollutant)
        pm2Status = pm2Query.get()
        
        htmlReturnValue = '<h2><span class="pollutantName">'
        htmlReturnValue += pollutant
        htmlReturnValue += "</span>"
        htmlReturnValue += '&nbsp;&nbsp;<span class="lastUpdatedTime">(Updated at '
        htmlReturnValue += str(pm2Status.date)
        htmlReturnValue += ')</span>'
        htmlReturnValue += "</h2><div><em>"+pm2Status.description+"</em></div>"
        htmlReturnValue += "<div>Concentration: <span>"+str(pm2Status.concentration)+"</span></div>"
        htmlReturnValue += "<div>AQI: <span>"+str(pm2Status.aqi)+"</span></div>"

        return htmlReturnValue

class UpdateStatusFromTwitter(webapp.RequestHandler):
    def get(self):
        statuses = twitter.getRecentStatuses()

        for status in statuses:
            # Example status: "03-05-2010; 13:00; PM2.5; 17.0; 55; Moderate // Ozone; 43.3; 36; Good"
            statusArray = status.split(";")
            statusArray.insert(5, statusArray[5].split("//")[0])
            statusArray[6] = statusArray[6].split("//")[1]
            statusArray = map((lambda str: str.strip()),statusArray)
            year = int(statusArray[0].split("-")[2])
            day = int(statusArray[0].split("-")[1])
            month = int(statusArray[0].split("-")[0])
            hour = int(statusArray[1][0:2])
            updateDateTime = datetime.datetime(year, month, day, hour)
            for i in range(2, len(statusArray), 4):
                newPollutantStatus = PollutantStatus(
                    type = statusArray[i],
                    date = updateDateTime,
                    description = statusArray[i+3],
                    concentration = float(statusArray[i+1]),
                    aqi = int(statusArray[i+2]))
                
                # Ensure that we aren't accidentally adding a duplicate status to
                # the database
                if PollutantStatus.gql("WHERE type = :1 AND date = :2", newPollutantStatus.type, newPollutantStatus.date).count() < 1:
                    newPollutantStatus.put()
                else:
                    self.response.out.write("Duplicate status detected<br />")
                    logging.info("Duplicate status detected: "+newPollutantStatus.type+" "+str(newPollutantStatus.date));
        self.response.out.write("Updated with "+status)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/tasks/updateStatus', UpdateStatusFromTwitter)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
