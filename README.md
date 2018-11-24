# brewfather plugin for CraftBeerPi 3.0
Update Brewfather batch fermentation data from CraftBeerPi3 Tilt devices.
Currently the code handles RED and PINK Tilt devices.

## Pre-requisites
Brewfather https://web.brewfather.app

CraftBeerPi 3.0 https://github.com/Manuel83/craftbeerpi3

## Configuration for BrewFather
Go to the settings menu and enable iSpindel.
Brewfather will allocate a device_id for your iSpindel.
The id will appear in the server url right after the /ispindel?id=

The id will look something like "d3gKTeZ43MP09T"

## Configuration for CraftBeerPi
1. In CraftBeerPi3 set up iSpindel as four sensors.
    1. Temperatue
    2. Gravity
    3. Battery
    4. RSSI
2. Make sure the device reports data to CraftBeerPi3.
    You may want to calibrate the iSpindel at this point.
3. Download this plugin into the craftbeerpi3/modules/plugins directory and
    restart CraftBeerPi3

## CraftBeerPi3 Parameters
Set the brewfather_iSpindel_id to the one BrewFather provided you.

## Results
    1. Logging occurs every 15 minutes. Wait a while for some values to log.
    2. Go to the Fermenting tab of the Brewfather Batches for
    the relevant batch. The graph will show logged
    temperature and Gravity values
    3. The Edit button will show individual logged results
    and the comment.
