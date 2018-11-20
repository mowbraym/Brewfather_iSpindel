# brewfather craftbeerpi3 plugin
# Log iSpindel temperature, SG and Battery data from CraftBeerPi 3.0 to the brewfather app
# https://brewfather.app/
#
# Note this code is heavily based on the Thingspeak plugin by Atle Ravndal
# and I acknowledge his efforts have made the creation of this plugin possible
# It is also now heavily based on the BrewStat.us and Brewfather modules I've written
#
from modules import cbpi
from thread import start_new_thread
import logging
import requests
import datetime

DEBUG = False
drop_first = None

# Parameters
brewfather_iSPindel_id = None

def log(s):
    if DEBUG:
        s = "brewfather_iSPindel: " + s
        cbpi.app.logger.info(s)

@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("brewfather_iSPindel plugin Initialize")
    log("Brewfather_iSPindel params")
# the unique id value (the bit following id= in the "Cloud URL" in the setting screen
    global brewfather_iSPindel_id

    brewfather_iSPindel_id = cbpi.get_config_parameter("brewfather_iSPindel_id", None)
    log("Brewfather brewfather_iSPindel_id %s" % brewfather_iSPindel_id)

    if brewfather_iSPindel_id is None:
	log("Init brewfather_iSPindel config URL")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_iSPindel_id", "", "text", "Brewfather_iSPindel id")
	except:
	    cbpi.notify("Brewfather_iSPindel Error", "Unable to update Brewfather_iSPindel id parameter", type="danger")
    log("Brewfather_iSPindel params ends")

# interval=900 is 900 seconds, 15 minutes, same as the Tilt Android App logs.
# if you try to reduce this, brewfather will throw "ignored" status back at you
@cbpi.backgroundtask(key="brewfather_iSPindel_task", interval=900)
def brewfather_iSPindel_background_task(api):
    log("brewfather_iSPindel background task")
    global drop_first
    if drop_first is None:
        drop_first = False
        return False

    if brewfather_iSPindel_id is None:
        return False

    now = datetime.datetime.now()
    for key, value in cbpi.cache.get("sensors").iteritems():
	log("key %s value.name %s value.instance.last_value %s value.type %s value.instance.sensorType %s" % (key, value.name, value.instance.last_value, value.type, value.instance.sensorType))
#
# TODO: IMPORTANT - Temp sensor must be defined preceeding Gravity sensor and 
#		    each Tilt must be defined as a pair without another Tilt
#		    defined between them, e.g.
#			RED Temperature
#			RED Gravity
#			PINK Temperature
#			PINK Gravity
#
	if (value.type == "iSPindel"):
	    if (value.instance.sensorType == "Temperature"):
# A Tilt Temperature device is the first of the Tilt pair of sensors so
#    reset the data block to empty
		payload = "{ "
		payload += " \"name\": \"%s\",\r\n" % value.name
		payload += " \"ID\": \"%s\",\r\n" % value.id
		temp = value.instance.last_value
# brewfather expects *F so convert back if we use C
		if (cbpi.get_config_parameter("unit",None) == "C"):
		    temp = value.instance.last_value * 1.8 + 32
                payload += " \"temperature\": \"%s\",\r\n" % temp
# might squeeze a battery device in here and make iSpindel a trio of logical devices
		if (value.instance.sensorType == "Gravity"):
                payload += " \"gravity\": \"%s\",\r\n" % value.instance.last_value
                payload += " \"interval\": \"900\",\r\n"
                payload += " \"RSSI\": \"-96\" }"
		log("Payload %s" % payload)
		url = "http://log.brewfather.net/ispindel"
		headers = {
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }
		id = cbpi.get_config_parameter("brewfather_iSpindel_id", None)
		querystring = {"id":id}
		r = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		log("Result %s" % r.text)
    log("brewfather_iSpindel done")
