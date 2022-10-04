import time, json, urllib.request, datetime
# The requests by default use epoch, altough you could change this to something else
epoch_time = int(time.time())
# The IP adress of the device
ipaddress  = "192.168.2.254"
# Get the general attributes
tesydata   = ["devstat", "status", "getAccessories", "mtProfile", "inettest", "getVolume", "watt", "getVacation", "calcRes", "apsecret"]
# Get the schedules from the device
tesyshdata = ["getP3", "getP2", "getP1"]
# A place to store the data we get back
tesyreturn = {}
tesyshed1  = []
tesyshed2  = []
tesyshed3  = []

class tesy():
    """
    A simple class to display all the data of your tesy boiler.
    Maybe even change a thing or two.
    """

    # All tesy requests require current epoch.
    epoch_time = int(time.time())

    def __init__(self):
        super(tesy, self).__init__()
        self._scan_device(ipaddress)
        self._weekly_schedule(tesyreturn['mode'])

    def _scan_device(self, ip):
        # This function will get all the data from the boiler.
        for stat in tesydata:
            turl = f"http://{ip}/{stat}?_={epoch_time}"
            with urllib.request.urlopen(turl) as url:
                data = json.loads(url.read().decode())
                #print(f"Getting: {stat}")
                tesyreturn.update(data)

        for sched in tesyshdata:
            turl = f"http://{ip}/{sched}?_={epoch_time}"
            with urllib.request.urlopen(turl) as url:
                data = json.loads(url.read().decode())
                #print(f"Getting: {sched}")
                if sched == "getP1":
                    tesyshed1.extend(data)
                elif sched == "getP2":
                    tesyshed2.extend(data)
                elif sched == "getP3":
                    tesyshed3.extend(data)
                else:
                    print("Schedule not known")

    def _weekly_schedule(self, id):
        calculate = True
        if id == '2':
            schedule = tesyshed1
        elif id == '3':
            schedule = tesyshed2
        elif id == '4':
            schedule = tesyshed3
        else:
            schedule = ""
            calculate = False

        if calculate == True:
            current_day = list(schedule[datetime.datetime.today().weekday()])[0]
            day = schedule[datetime.datetime.today().weekday()]
            hours = day[current_day]
            next_hour = "h" + str(datetime.datetime.today().hour + 1)
            next_hour_c = datetime.datetime.today().hour + 1
            #current_hour = "h" + str(datetime.datetime.today().hour)
            #target_temp  = hours[current_hour]
            next_target_temp  = hours[next_hour]
        else:
            # It is possible that these are not needed, but
            #there is no "Schedule" for the other modes as far as i can tell
            next_target_temp = "NA"
            next_hour        = "NA"
            next_hour_c      = "NA"

        data = {"next_target": next_target_temp, "next_hour": next_hour, "next_hour_c": next_hour_c}
        tesyreturn.update(data)

    @property
    def tesyprinter(self):
        # Prints all the data
        return tesyreturn

    @property
    def tesyprinters1(self):
        # Prints all the data of schedule 1
        return tesyshed1

    @property
    def tesyprinters2(self):
        # Prints all the data of schedule 2
        return tesyshed2

    @property
    def tesyprinters3(self):
        # Prints all the data of schedule 3
        return tesyshed3

#    @property
#    def pickle(self):
#        import sqlite3 as sl
#        con = sl.connect('tesy.db')
#        CREATE TABLE IF NOT EXISTS tesy (date date, power text, powerst text, temp integer, target integer, boost, integer, kwh1 integer, kwh2 integer);
#        data = [
#                tesyreturn['date'],
#                tesyreturn['power_sw'],
#                tesyreturn['heater_state'],
#                tesyreturn['gradus'],
#                tesyreturn['ref_gradus'],
#                tesyreturn['boost'],
#                tesyreturn['ltc'],
#                tesyreturn['kwh']
#            ]
#        print(data)


    @property
    def tesyprettyprinter(self):
        # Prints all the data but pretty
        pretty = f"""
        ==========================================
        # General:                               #
        ==========================================
        | Temp:  {tesyreturn['gradus'][0:4]:^4} | Target: {tesyreturn['ref_gradus'][0:2]:^4} |
        | Next Temp: {tesyreturn['next_target']} at {tesyreturn['next_hour_c']}:00
        | Boost: {tesyreturn['boost'][0:4]:^4} | Power: {tesyreturn['power_sw'][0:4]:^4}  | State: {tesyreturn['heater_state'][0:7]:^7}
        | Errors: {tesyreturn['err_flag'][0:4]:^4} | Liters: {tesyreturn['liters'][0:3]:^3} |
        | TimeZone: {tesyreturn['tz'][0:4]:^4}
        | Local Time: {tesyreturn['date']}
        ==========================================
        # Power Usage:                           #
        ==========================================
        | Alltime KWH: {tesyreturn['ltc'][0:4]:^4}
        | Current KWH: {tesyreturn['kwh'][0:4]:^4}
        | Max Power: {tesyreturn['powerh'][0:4]:^4}
        | Counter Reset: {tesyreturn['resetDate']}
        ==========================================
        # MyTesy:                                #
        ==========================================
        | MyTDesc: {tesyreturn['mtDesc'][0:28]:^28}
        | MyTEmail: {tesyreturn['mtEmail'][0:28]:^28}
        | MyTDetail: {tesyreturn['mtDetail'][0:28]:^28}
        ==========================================
        # Vacation:                              #
        ==========================================
        | Vacation Set: {tesyreturn['vSet'][0:4]:^4}
        | Vacation Target Temp: {tesyreturn['vTemp'][0:4]:^4}
        | Vacation date (Y:M:D:H): {tesyreturn['vYear']}:{tesyreturn['vMonth']}:{tesyreturn['vMDay']}:{tesyreturn['vHour']}
        | Vacation WeekDay: {tesyreturn['vWDay']}
        ==========================================
        # Wifi: (outgoing)                       #
        ==========================================
        | Errors: {tesyreturn['err'][0:4]:^4}
        | Conected: {tesyreturn['connection'][0:4]:^4}
        | Signal: {tesyreturn['signal'][0:4]:^4}
        | SSID: {tesyreturn['essid'][0:28]:^28}
        | Internet: {tesyreturn['inet'][0:28]:^28}
        ==========================================
        # Wifi: (Indoor)                         #
        ==========================================
        | Protection: {tesyreturn['apEnc'][0:28]:^28}
        | Password:  {tesyreturn['apText'][0:28]:^28}
        ==========================================
        # Misc:                                  #
        ==========================================
        | DevID: {tesyreturn['devid'][0:28]:^28}
        | MacAddr: {tesyreturn['macaddr'][0:28]:^28}
        """

        return pretty


if __name__ == "__main__":
    tesy = tesy()

    #(f"Tesy data: {tesy.tesyprinters1}")
    print(f"{tesy.tesyprettyprinter}")
#    tesy.pickle
