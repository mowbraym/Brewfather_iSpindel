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
brewfather_comment = None
brewfather_id = None

def log(s):
    if DEBUG:
        s = "brewfather: " + s
        cbpi.app.logger.info(s)

@cbpi.initalizer(order=9000)
def init(cbpi):
    cbpi.app.logger.info("brewfather plugin Initialize")
    log("Brewfather params")
# the comment that goes along with each post (visible in the edit data screen)
    global brewfather_comment
# the unique id value (the bit following id= in the "Cloud URL" in the setting screen
    global brewfather_id

    brewfather_comment = cbpi.get_config_parameter("brewfather_comment", None)
    log("Brewfather brewfather_comment %s" % brewfather_comment)
    brewfather_id = cbpi.get_config_parameter("brewfather_id", None)
    log("Brewfather brewfather_id %s" % brewfather_id)

    if brewfather_comment is None:
	log("Init brewfather config Comment")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_comment", "", "text", "Brewfather comment")
	except:
	    cbpi.notify("Brewfather Error", "Unable to update Brewfather comment parameter", type="danger")
    if brewfather_id is None:
	log("Init brewfather config URL")
	try:
# TODO: is param2 a default value?
	    cbpi.add_config_parameter("brewfather_id", "", "text", "Brewfather id")
	except:
	    cbpi.notify("Brewfather Error", "Unable to update Brewfather id parameter", type="danger")
    log("Brewfather params ends")

# interval=900 is 900 seconds, 15 minutes, same as the Tilt Android App logs.
# if you try to reduce this, brewfather will throw "ignored" status back at you
@cbpi.backgroundtask(key="brewfather_task", interval=900)
def brewfather_background_task(api):
    log("brewfather background task")
    global drop_first
    if drop_first is None:
        drop_first = False
        return False

    if brewfather_id is None:
        return False

    now = datetime.datetime.now()
    for key, value in cbpi.cache.get("sensors").iteritems():
	log("key %s value.name %s value.instance.last_value %s" % (key, value.name, value.instance.last_value))
#
# TODO: IMPORTANT - Temp sensor must be defined preceeding Gravity sensor and 
#		    each Tilt must be defined as a pair without another Tilt
#		    defined between them, e.g.
#			RED Temperature
#			RED Gravity
#			PINK Temperature
#			PINK Gravity
#
	if (value.type == "TiltHydrometer"):
	    if (value.instance.sensorType == "Temperature"):
# A Tilt Temperature device is the first of the Tilt pair of sensors so
#    reset the data block to empty
		payload = "{ "
# generate timestamp in "Excel" format
		timepoint = now.toordinal() - 693594 + (60*60*now.hour + 60*now.minute + now.second)/float(24*60*60)
		payload += " \"Timepoint\": \"%s\",\r\n" % timepoint
		payload += " \"Color\": \"%s\",\r\n" % value.instance.color
## TODO: would this work here? data['beer'] = cbpi.get_config_parameter("brewfather_%s" % value.instance.color, None)
		payload += " \"Beer\": \"\",\r\n"
# 2018.11.09 - End Changed code
		temp = value.instance.last_value
# brewfather expects *F so convert back if we use C
		if (cbpi.get_config_parameter("unit",None) == "C"):
		    temp = value.instance.last_value * 1.8 + 32
                payload += " \"Temp\": \"%s\",\r\n" % temp
	    if (value.instance.sensorType == "Gravity"):
                payload += " \"SG\": \"%s\",\r\n" % value.instance.last_value
                payload += " \"Comment\": \"%s\" }" % cbpi.get_config_parameter("brewfather_comment", None)
		log("Payload %s" % payload)
		url = "http://log.brewfather.net/tilt"
		headers = {
		    'Content-Type': "application/json",
		    'Cache-Control': "no-cache"
		    }
		id = cbpi.get_config_parameter("brewfather_id", None)
		querystring = {"id":id}
		r = requests.request("POST", url, data=payload, headers=headers, params=querystring)
		log("Result %s" % r.text)
    log("brewfather done")
