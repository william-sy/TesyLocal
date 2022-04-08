# TesyLocal
The opposite of Tesy cloud


## Intro
This little package only reads data from your tesy boiler at the moment.

Requirements: Python3.6 and up

Currently can give you this data:

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
| Vacation date (Y:M:D:H): 21:12:12:1:20
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
| Password:          Password
==========================================
# Misc:                                  #
==========================================
| DevID:  2004-3402 FW21.21
| MacAddr:      70:f1:
```

Mode:
1: Manual mode
2: Weekly program 1
3: Weekly program 2
4: Weekly program 3
5: Eco 1
6: Eco 2
7: Eco 3
