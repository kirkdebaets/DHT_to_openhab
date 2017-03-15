#!/usr/bin/python

import glob
import json
import os
import sys
import urllib2
import yaml
import Adafruit_DHT

# class for handling the posting
# I stole this from somewhere but cannot remember where for attribution
class MethodRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self, *args, **kwargs)

def getConfig():
    # read the DHT.yaml file from my .config directory
    # doing this in multiple steps because there is no way I'll remember this
    # after I have put the code away for a while and I don't want to spend time
    # in the future to untangle this
    thisScript = os.path.abspath(__file__)
    cwd = os.path.dirname(thisScript)
    parentDirectory = os.path.split(cwd)[0]
    configFile = os.path.join(parentDirectory, '.config', 'DHT.yaml')

    with open(configFile, 'r') as f:
        settings = yaml.load(f)

    return settings

def getReadings():

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(deviceType, pin)

    # convert the temperature to Fahrenheit.
    temperature = temperature * 9/5.0 + 32

    # Note from Adafruit:  Sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    if humidity is not None and temperature is not None:
        print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
        return [temperature, humidity]
    else:
        print 'Failed to get reading. Try again!'
    # we'll get'em next time
        sys.exit(1)

def postToOpenhab(Turl,payload):
    #print str(Turl)
    # need a PUT instead of a POST
    request = MethodRequest(Turl, method='PUT')
    request.add_header('Content-Type', 'text/plain')
    request.add_data(payload)

    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        if hasattr(e,'reason'):
            print "There was an URL error: " + str(e.reason)
            return
        elif hasattr(e,'code'):
            print "There was an HTTP error: " + str(e.code)
            return

#------------------------------------------------------
# Mainline
#------------------------------------------------------
if __name__ == '__main__':
    setting = getConfig()

    deviceType = setting["device_type"]
    pin = setting["gpio_pin"]
    baseUrl = setting["base_url"]
    temperatureItem = setting["temperature_item_name"]
    humidityItem = setting["humidity_item_name"]
    temperatureUrl = baseUrl + '/rest/items/' + temperatureItem + '/state'
    humidityUrl = baseUrl + '/rest/items/' + humidityItem + '/state'

    [measuredTemp, measuredHumidity] = getReadings()
    packedTemp = json.dumps(measuredTemp)
    packedHumidity = json.dumps(measuredHumidity)

    postToOpenhab(temperatureUrl,packedTemp)
    postToOpenhab(humidityUrl,packedHumidity)
