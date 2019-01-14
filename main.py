import requests, datetime

poll = ["VA/Ashburn",
        "VA/Sterling",
        "VA/Aldie",
        "VA/Purcellville",
        "VA/Lovettsville"]

apikey = "API KEY"
weather = {}
dailyscore = {}
locscore = {}
avgscore = {}

def pullWeather(loc):
    r = requests.get("http://api.wunderground.com/api/" + apikey + "/forecast10day/q/" + loc + ".json")
    r = r.json()["forecast"]["simpleforecast"]["forecastday"]
    weather[loc] = r

def scoreWeather(loc):
    tscore = {}
    locweather = weather[loc]
    for w in locweather:
        date = w["date"]["epoch"]
        #score conditions
        conScore = 0.0
        if "rain" in w["icon"]:
            conScore = .5
        if "snow" in w["icon"]:
            conScore = 1
        if w["maxwind"]["mph"] > 25:
            conScore = (conScore + .25) * 2
        if (w["snow_allday"]["in"] > 1) and (w["snow_allday"]["in"] < 2):
            conScore = conScore * 1.25
        if (w["snow_allday"]["in"] > 2):
            conScore = w["snow_allday"]["in"]
        if (w["snow_allday"]["in"] < 1):
            conScore = conScore * .75
        #score temperature
        tempScore = 1.0
        if w["low"]["fahrenheit"] == "":
            w["low"]["fahrenheit"] = w["high"]["fahrenheit"]
        if w["high"]["fahrenheit"] == "":
            w["high"]["fahrenheit"] = w["low"]["fahrenheit"]
        if ((int(w["low"]["fahrenheit"]) + int(w["high"]["fahrenheit"])) / 2) < 32:
            tempScore = tempScore * 2
        if ((int(w["low"]["fahrenheit"]) + int(w["high"]["fahrenheit"])) / 2) > 40:
            tempScore = 0.0
        if (int(w["low"]["fahrenheit"])) < 25:
            tempScore = tempScore * 1.25
        if (int(w["low"]["fahrenheit"])) < 20:
            tempScore = tempScore * 1.5
        if (int(w["low"]["fahrenheit"])) > 32:
            tempScore = -1.25

        score = (conScore * .80) + (tempScore * .20)
        if score < 0:
            score = 0
        tscore[date] = round(score, 3)

    for date in tscore:
        if date not in locscore:
            locscore[date] = {}
        locscore[date][loc] = tscore[date]

def calculateScore():
    for date in sorted(locscore):
        score = 0
        count = 1
        for loc in locscore[date]:
            score = score + locscore[date][loc]
        avgscore[date] = score / len(locscore[date])
    score = 0
    count = 1
    for date in sorted(avgscore):
        if (avgscore[date] >= 1):
            score = score + avgscore[date]
            count = 1
        else:
            score = score * avgscore[date]
        dailyscore[date] = score / (count**2)
        count = count + 1

print "Retrieving Weather"
for loc in poll:
        pullWeather(loc)
print "Scoring Weather"
for loc in weather:
    scoreWeather(loc)
print "Calculating Daily Score"
calculateScore()
print ""
for key in sorted(dailyscore):
    date = datetime.datetime.fromtimestamp(int(key)).strftime('%a %m/%d')
    score = round(dailyscore[key] * 100, 2)
    if score > 100:
        score = 100
    print str(date) + ": " + str(score) + "%" + " (" + str(round(avgscore[key], 2)) + " / " + str(round(dailyscore[key], 2)) + ")"
