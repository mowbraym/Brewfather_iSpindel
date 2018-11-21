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

DEBUG = True
drop_first = None

# Parameters
brewfather_iSpindel_id = None

def log(s):
    if DEBUG:
        s = "brewfather_iSpindel: " + s
        cbpi.app.logger.info(s)

@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("brewfather_iSpindel plugin Initialize")
    log("Brewfather_iSpindel params")
# the unique id value (the bit following id= in the "Cloud URL" in the setting screen
    global brewfather_iSpindel_id

    brewfather_iSpindel_id = cbpi.get_config_parameter("brewfather_iSpindel_id", None)
    log("Brewfather brewfather_iSpindel_id %s" % brewfather_iSpindel_id)

    if brewfather_iSpindel_id is None:
	log("Init brewfather_iSpindel config URL")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_iSpindel_id", "", "text", "Brewfather_iSpindel id")
	except:
	    cbpi.notify("Brewfather_iSpindel Error", "Unable to update Brewfather_iSpindel id parameter", type="danger")
    log("Brewfather_iSpindel params ends")

# interval=900 is 900 seconds, 15 minutes, same as the Tilt Android App logs.
# if you try to reduce this, brewfather will throw "ignored" status back at you
@cbpi.backgroundtask(key="brewfather_iSpindel_task", interval=900)
def brewfather_iSpindel_background_task(api):
    log("brewfather_iSpindel background task")
    global drop_first
    if drop_first is None:
        drop_first = False
        return False

    if brewfather_iSpindel_id is None:
        return False

    now = datetime.datetime.now()
    for key, value in cbpi.cache.get("sensors").iteritems():
	log("key %s value.name %s value.instance.last_value %s value.type %s" % (key, value.name, value.instance.last_value, value.type))
#
# TODO: IMPORTANT - Temp sensor must be defined preceeding Gravity sensor and 
#		    each Tilt must be defined as a pair without another Tilt
#		    defined between them, e.g.
#			RED Temperature
#			RED Gravity
#			PINK Temperature
#			PINK Gravity
#
	if (value.type == "iSpindel"):
	    if (value.instance.sensorType == "Temperature"):
# A Tilt Temperature device is the first of the Tilt pair of sensors so
#    reset the data block to empty
		payload = "{ "
		payload += " \"name\": \"%s\",\r\n" % value.instance.name
		payload += " \"ID\": \"%s\",\r\n" % value.instance.id
#		payload += " \"angle\": \"%s\",\r\n" % value.instance.angle
		temp = value.instance.last_value
# brewfather expects *F so convert back if we use C
		if (cbpi.get_config_parameter("unit",None) == "C"):
		    temp = value.instance.last_value * 1.8 + 32
                payload += " \"temperature\": \"%s\",\r\n" % temp
	    if (value.instance.sensorType == "Battery"):
                payload += " \"battery\": \"%s\",\r\n" % value.instance.last_value
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
