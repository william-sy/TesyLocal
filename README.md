# TesyLocal
The opposite of Tesy cloud

## Intro
This little package only reads data from your tesy boiler at the moment.

Requirements:
- Python3.6 and up
- Boiler firmware of 20.20 and up

Currently this program will give you this:

```text
==========================================
# General:                               #
==========================================
| Temp:  53.0 | Target:  50  |
| Next Temp: 50 at 14:00
| Boost:  0   | Power:  on   | State:  READY
| Errors:  0   | Liters: 100 |
| TimeZone: CEST
| Local Time: 2022-04-08 13:27
==========================================
# Power Usage:                           #
==========================================
| Alltime KWH: 0.80
| Current KWH: 0.06
| Max Power: 2400
| Counter Reset: 2022-04-08 10:55:45
==========================================
# MyTesy:                                #
==========================================
| MyTDesc:           boiler1
| MyTEmail: noreply@yourdomain.com
| MyTDetail:
==========================================
# Vacation:                              #
==========================================
| Vacation Set:  0
| Vacation Target Temp:  70
| Vacation date (Y:M:D:H): 21:12:1:20
| Vacation WeekDay: 3
==========================================
# Wifi: (outgoing)                       #
==========================================
| Errors:  0
| Conected:  1
| Signal: -41
| SSID:       SSSIDDDD
| Internet:              1
==========================================
# Wifi: (Indoor)                         #
==========================================
| Protection:             psk2
| Password:               Password
==========================================
# Misc:                                  #
==========================================
| DevID:  2004-3402 FW21.21
| MacAddr:      70:f1:
```

## Boiler modes:
```text
1: Manual mode
2: Weekly program 1
3: Weekly program 2
4: Weekly program 3
5: Eco 1
6: Eco 2
7: Eco 3
8: ?
9: Vacation
```
> Note that there are a total of 9 modes, Not sure what they all do.


## Simple how-to get started / command examples:

```python
# This is a small app, using the TesyLocal module
from tesylocal import tesy
# Please specify your boiler IP like so, and if you want a initial sync of all values
## NOTE: This is only important if you are not planning to integrate this.
boiler = tesy("192.168.1.1", "sync")
# No sync:
boiler = tesy("192.168.1.1", "nosync")
# Then print a property, This requires "sync" or updateallvalues / updateschedules after connecting.
print(boiler.tesyprettyprinter)

## Other options:
# Update values:
boiler.updateallvalues('192.168.2.254')
boiler.updateschedules('192.168.2.254')
# Got DHCP?, Or perhaps you want to validate the IP once in a while or check if the device is alive:
boiler.check_ip_status('192.168.2.254')
# Turn on the boiler
boiler.boileronoff("192.168.2.254","on")
# Turn the boiler off
boiler.boileronoff("192.168.2.254","off")
# More are available:
# boostonoff, boilermanualmode, boileronoff, manualtemp,
# automanualmode, boilermode, resetpower, settime
boiler.boostonoff.__doc__
# for more info on a item.
```

## Home Assistant
Currently a integration is in the works, but until then you can add the following to your configuration.yaml
> Note that the `?_=1634912123253` (epoch) is a identifier to track your request, it is not needed to control the boiler.

``` yaml
rest_command:
  tsmt:
    url: "http://192.168.2.254/setTemp?val={{ temperature }}"
    method: GET

automation:
  - alias: "Tesy Temperature input automatically changed"
    trigger:
      platform: state
      entity_id: sensor.tesyboilertargettemp
    action:
      service: input_number.set_value
      target:
        entity_id: input_number.tesyboilermanualtempinput
      data:
        value: "{{ trigger.to_state.state }}"
  - alias: "Tesy Temperature input manually changed"
    trigger:
      platform: state
      entity_id: input_number.tesyboilermanualtempinput
    action:
      service: rest_command.tsmt
      data:
        temperature: "{{ trigger.to_state.state }}"

input_number:
  tesyboilermanualtempinput:
    name: Set Tesy Manual Temp
    min: 14
    max: 75
    step: 1
    unit_of_measurement: "°C"
    icon: mdi:temperature-celsius

switch:
  - platform: command_line
    switches:
      tesyboostonoff:
        command_on: "/usr/bin/curl -X GET http://192.168.2.254/boostSW?mode=1"
        command_off: "/usr/bin/curl -X GET http://192.168.2.254/boostSW?mode=0"
        command_state: "/usr/bin/curl -sX GET http://192.168.2.254/status"
        value_template: "{{ value_json['boost'] == '1' }}"
        friendly_name: Boost Tesy!
        icon_template: >
          {% if value_json['boost'] == '0' %} mdi:rocket
          {% elif value_json['boost'] == '1' %} mdi:rocket-launch
          {% else %} mdi:help-circle
          {% endif %}
      tesyonoff:
        command_on: "/usr/bin/curl -X GET http://192.168.2.254/power?val=on"
        command_off: "/usr/bin/curl -X GET http://192.168.2.254/power?val=off"
        command_state: "/usr/bin/curl -sX GET http://192.168.2.254/status"
        value_template: "{{ value_json['power_sw'] == 'on' }}"
        friendly_name: Tesy power switch!
        icon_template: >
          {% if value_json['power_sw'] == "on" %} mdi:toggle-switch
          {% else %} mdi:toggle-switch-off
          {% endif %}
      tesyresetpower:
        command_on: "/usr/bin/curl -X GET http://192.168.2.254/resetPow"
        friendly_name: Tesy power Reset!
      tesysetsetmanualmode:
        command_on: "/usr/bin/curl -X GET http://192.168.2.254/modeSW?mode=1"
        # Set a default schedule here if you dont want manual mode any longer
        command_off: "/usr/bin/curl -X GET http://192.168.2.254/modeSW?mode=2"
        command_state: "/usr/bin/curl -sX GET http://192.168.2.254/status"
        value_template: "{{ value_json['mode'] == '1' }}"
        friendly_name: Set Tesy manual mode
        icon_template: >
          {% if value_json['mode'] == '1' %} mdi:water-boiler
          {% elif value_json['mode'] == '2' %} mdi:calendar
          {% elif value_json['mode'] == '3' %} mdi:calendar
          {% elif value_json['mode'] == '4' %} mdi:calendar
          {% elif value_json['mode'] == '5' %} mdi:sprout
          {% elif value_json['mode'] == '6' %} mdi:sprout
          {% elif value_json['mode'] == '7' %} mdi:sprout
          # No idea what mode 8 is.
          {% elif value_json['mode'] == '8' %} mdi:help
          {% elif value_json['mode'] == '9' %} mdi:beach
          {% else %} mdi:help-circle
          {% endif %}
sensor:
  - platform: rest
    resource: http://192.168.2.254/status
    name: tesyboiler
    method: GET
    value_template: "OK"
    json_attributes:
      - gradus
      - ref_gradus
      - heater_state
      - err_flag
      - boost
      - power_sw
      - volume
      - watts
      - mode
  - platform: rest
    resource: http://192.168.2.254/calcRes
    name: tesyboilerpower
    method: GET
    value_template: "OK"
    json_attributes:
      - kwh
      - ltc
      - resetDate

template:
  - sensor:
      - name: "Boiler kWh all time"
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: "{{ states('sensor.TesyBoilerKwhAllTime') }}"
  - sensor:
      - name: "tesyboilerkwhresetdate"
        icon: mdi:calendar-blank-outline
        unique_id: "TesyBoilerKwhResetDate"
        state: "{{ state_attr('sensor.tesyboilerpower', 'resetDate') }}"
  - sensor:
      - name: "tesyboilerkwhafterreset"
        icon: mdi:lightning-bolt
        unique_id: "TesyBoilerKwhAfterReset"
        state: "{{ state_attr('sensor.tesyboilerpower', 'kwh') }}"
        unit_of_measurement: "kWh"
        device_class: energy
  - sensor:
      - name: "tesyboilerwatervolume"
        icon: mdi:cup-water
        unique_id: "TesyBoilerWaterVolume"
        state: "{{ state_attr('sensor.tesyboiler', 'volume') }}"
        unit_of_measurement: "L"
  - sensor:
      - name: "tesyboilerwatts"
        icon: mdi:power-plug
        unique_id: "TesyBoilerWatts"
        state: "{{ state_attr('sensor.tesyboiler', 'watts') }}"
        unit_of_measurement: "W"
  - sensor:
      - name: "tesyboilermode"
        icon: mdi:calendar
        unique_id: "TesyBoilerMode"
        state: "{{ state_attr('sensor.tesyboiler', 'mode') }}"
  - sensor:
      - name: "tesyboilererror"
        icon: mdi:water-boiler-alert
        unique_id: "TesyBoilerError"
        state: "{{ state_attr('sensor.tesyboiler', 'err_flag') }}"
  - sensor:
      - name: "tesyboilerboost"
        icon: mdi:arrow-up-circle
        unique_id: "TesyBoilerBoost"
        state: "{{ state_attr('sensor.tesyboiler', 'boost') }}"
  - sensor:
      - name: "tesyboileronoff"
        icon: mdi:help-circle
        unique_id: "TesyBoilerOnOff"
        state: "{{ state_attr('sensor.tesyboiler', 'power_sw') }}"
  - sensor:
      - name: "tesyboilerstate"
        icon: mdi:help-circle
        unique_id: "TesyBoilerState"
        state: "{{ state_attr('sensor.tesyboiler', 'heater_state') }}"
  - sensor:
      - name: "tesyboilertargettemp"
        icon: mdi:help-circle
        unique_id: "TesyBoilerTargetTemp"
        state: "{{ state_attr('sensor.tesyboiler', 'ref_gradus') }}"
  - sensor:
      - name: "tesyboilerwatertemp"
        icon: mdi:temperature-celsius
        unique_id: "TesyBoilerWaterTemp"
        state: "{{ state_attr('sensor.tesyboiler', 'gradus') }}"
        unit_of_measurement: "°C"
  - sensor:
      - name: "tesyboilerwatertargettemp"
        icon: mdi:temperature-celsius
        unique_id: "TesyBoilerWaterTargetTemp"
        state: "{{ state_attr('sensor.tesyboiler', 'ref_gradus') }}"
        unit_of_measurement: "°C"
  - sensor:
      - name: "tesyboilerkwhalltime"
        icon: mdi:lightning-bolt
        unique_id: "TesyBoilerKwhAllTime"
        state: "{{ state_attr('sensor.tesyboilerpower', 'ltc') }}"
        unit_of_measurement: "kWh"
        device_class: energy

```

## Notes:
Here are some of the URLs you can manually make to control the boiler and a description:
```text
1634911445424 == epoch

# boost on
http://192.168.2.254/boostSW?mode=0&_=1634911445424
# boost off
http://192.168.2.254/boostSW?mode=1&_=1634911446795
# set adaptive:
http://192.168.2.254/adaptive?val=
# Set antifreeze:
http://192.168.2.254/aantifrize?val=    # changeStatusParam, antifrost_enable   1 and 0
# Set lock:
http://192.168.2.254/lockKey?val=   # changeStatusParam lockB 1 and 0

# set to temp
http://192.168.2.254/setTemp?val=45&_=1634911879615
# manual mode
http://192.168.2.254/modeSW?mode=1&_=1634912123253
# set program 1
http://192.168.2.254/modeSW?mode=2&_=1634912027732
# set 2
http://192.168.2.254/modeSW?mode=3&_=1634912041121
# set 3
http://192.168.2.254/modeSW?mode=4&_=1634912071235
# eco 1
http://192.168.2.254/modeSW?mode=5&_=1634912151669
# eco 2
http://192.168.2.254/modeSW?mode=6&_=1634912164061
# eco 3
http://192.168.2.254/modeSW?mode=7&_=1634912180802
# device status
http://192.168.2.254/devstat?_=1634923248104
# get status
http://192.168.2.254/status?_=1634911418801
language+ set up status
http://192.168.2.254/getAccessories?_=1634923248606
# Set volume
http://192.168.2.254/setVolume?_=1634912180802&liters=100
# my tesy profile
http://192.168.2.254/mtProfile?_=1634911562552
# internet test
http://192.168.2.254/inettest?_=1634911553629
# kwh info
http://192.168.2.254/calcRes?&watt=&_=1634911625571
http://192.168.2.254/calcRes&_=1634911625571
# get volume
http://192.168.2.254/getVolume?_=1634911621820
# get schedule program 3
http://192.168.2.254/getP3?_=1634911711930
# get schedule program 2
http://192.168.2.254/getP2?_=1634911711930
# get schedule program 1
http://192.168.2.254/getP1?_=1634911711930
# get vacation
http://192.168.2.254/getVacation?_=1634911711432
# reset power
http://192.168.2.254/resetPow?_=1634912213060
# get power capacity
http://192.168.2.254/watt?_=1634912213060
# set power
http://192.168.2.254/power?val=1000&_=1634912213060

# Set vacation
# 30 december 2021 till 02:00 set to 70 This is day number 4 of the week sunday = 0 monday = 1,,
http://192.168.2.254/setVacation?_=1634990836894&vYear=21&vMonth=12&vMDay=30&vWDay=4&vHour=02&vTemp=70
# 1 december 2021 till 20:00 set to 70 This is day number 3 of the week sunday = 0 monday = 1,,
http://192.168.2.254/setVacation?_=1634990969916&vYear=21&vMonth=12&vMDay=1&vWDay=3&vHour=20&vTemp=70

# set a new item in the schedule:
http://192.168.2.254/setP1
+ body:
POST /setP1 HTTP/1.1
Host: 192.168.2.254
Connection: keep-alive
Content-Length: 1512
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Origin: http://192.168.2.254
Referer: http://192.168.2.254/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,nl;q=0.8
dnt: 1
sec-gpc: 1
&Mon00=30&Mon01=30&Mon02=30&Mon03=30&Mon04=30&Mon05=30&Mon06=30&Mon07=50&Mon08=50&Mon09=50&Mon10=40&Mon11=40&Mon12=50&Mon13=50&Mon14=40&Mon15=40&Mon16=40&Mon17=50&Mon18=50&Mon19=30&Mon20=30&Mon21=30&Mon22=30&Mon23=30&Tue00=30&Tue01=30&Tue02=30&Tue03=30&Tue04=30&Tue05=30&Tue06=30&Tue07=50&Tue08=50&Tue09=50&Tue10=40&Tue11=40&Tue12=50&Tue13=50&Tue14=40&Tue15=40&Tue16=40&Tue17=50&Tue18=50&Tue19=30&Tue20=30&Tue21=30&Tue22=30&Tue23=30&Wen00=30&Wen01=30&Wen02=30&Wen03=30&Wen04=30&Wen05=30&Wen06=30&Wen07=50&Wen08=50&Wen09=50&Wen10=40&Wen11=40&Wen12=50&Wen13=50&Wen14=40&Wen15=40&Wen16=40&Wen17=50&Wen18=50&Wen19=30&Wen20=30&Wen21=30&Wen22=30&Wen23=30&Thu00=30&Thu01=30&Thu02=30&Thu03=30&Thu04=30&Thu05=30&Thu06=30&Thu07=45&Thu08=45&Thu09=45&Thu10=45&Thu11=45&Thu12=45&Thu13=45&Thu14=45&Thu15=55&Thu16=65&Thu17=75&Thu18=75&Thu19=30&Thu20=30&Thu21=30&Thu22=30&Thu23=30&Fri00=30&Fri01=30&Fri02=30&Fri03=30&Fri04=30&Fri05=30&Fri06=30&Fri07=45&Fri08=45&Fri09=45&Fri10=35&Fri11=35&Fri12=45&Fri13=45&Fri14=35&Fri15=35&Fri16=35&Fri17=35&Fri18=45&Fri19=45&Fri20=55&Fri21=65&Fri22=75&Fri23=75&Sat00=30&Sat01=30&Sat02=30&Sat03=30&Sat04=30&Sat05=30&Sat06=30&Sat07=30&Sat08=30&Sat09=30&Sat10=50&Sat11=60&Sat12=60&Sat13=50&Sat14=50&Sat15=50&Sat16=50&Sat17=50&Sat18=50&Sat19=50&Sat20=50&Sat21=50&Sat22=50&Sat23=50&Sun00=30&Sun01=30&Sun02=30&Sun03=30&Sun04=30&Sun05=30&Sun06=30&Sun07=30&Sun08=30&Sun09=30&Sun10=50&Sun11=60&Sun12=60&Sun13=50&Sun14=50&Sun15=50&Sun16=50&Sun17=50&Sun18=50&Sun19=30&Sun20=30&Sun21=30&Sun22=30&Sun23=30

# update boiler time and date
http://192.168.2.254/setdate?tOffset=CET-1CEST,M3.5.0,M10.5.0/3&tDay=5&tMonth=10&tYear=2022&tHour=16&tMin=0&tSec=00?_=1664978401338
```
