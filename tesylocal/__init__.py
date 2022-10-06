# -*- coding: utf-8 -*-
## Imports:
import time, json, urllib.request, datetime, logging, platform, subprocess, os
from urllib.error import HTTPError, URLError
from socket import timeout
## Variables:
# A UUID accepteb by tesy:
epoch_time = int(time.time())
# For tessting:                                                        ipaddress  = "192.168.2.254"
# The length of the time out in secconds before giving up on a device:
urltimeout = 5
# Get the general attributes
tesydata   = ["devstat", "status", "getAccessories", "mtProfile", "inettest", "getVolume", "watt", "getVacation", "calcRes", "apsecret"]
# Get the schedules from the device
tesyshdata = ["getP3", "getP2", "getP1"]
# A place to store the data we get back
tesyreturn = {}
tesyshed1  = []
tesyshed2  = []
tesyshed3  = []

__version__ = "1.2"

NAME = "tesylocal"
VERSION = __version__
_LOGGER = logging.getLogger(NAME)

class tesy():
    """
    A simple class to display all the data of your tesy boiler.
    Maybe even change a thing or two.
    """

    def __init__(self, ipaddress, sync):
        super(tesy, self).__init__()
        self._validate_ip(ipaddress)
        if sync == "sync":
            self._scan_device(ipaddress)
            self._weekly_schedule(tesyreturn['mode'])
        else:
            pass

    def _validate_ip(self, ip):
        try:
            turl = f"http://{ip}/devstat"
            response = urllib.request.urlopen(turl, timeout=urltimeout).read().decode('utf-8')
        except HTTPError as error:
            logging.error('HTTP Error: Data of %s not retrieved because %s\nURL: %s', ip, error, turl)
        except URLError as error:
            if isinstance(error.reason, timeout):
                logging.error('Timeout Error: Data of %s not retrieved because %s\nURL: %s', ip, error, turl)
            else:
                logging.error('URL Error: Data of %s not retrieved because %s\nURL: %s', ip, error, turl)
        else:
            logging.info('Validation of the URl successful, Validating json')
            try:
                data = json.loads(response)
            except ValueError as error:
                logging.info('JSON Error: Could not load given JSON from URL: %s', error)
            else:
                try:
                    wifi = data['inetdev']
                except KeyError as error:
                    logging.info('JSON Error: Could not find inetdev key in JSON: %s', error)
                else:
                    logging.info('Validation of device completed')

    def _scan_device(self, ip):
        # This function will get all the data from the boiler.
        for stat in tesydata:
            turl = f"http://{ip}/{stat}"
            # By placing this at the end of the above URL you geive the URL a UUID.
            #?_={epoch_time}"
            with urllib.request.urlopen(turl) as url:
                data = json.loads(url.read().decode())
                tesyreturn.update(data)

        for sched in tesyshdata:
            turl = f"http://{ip}/{sched}"
            with urllib.request.urlopen(turl) as url:
                data = json.loads(url.read().decode())
                if sched == "getP1":
                    tesyshed1.extend(data)
                elif sched == "getP2":
                    tesyshed2.extend(data)
                elif sched == "getP3":
                    tesyshed3.extend(data)
                else:
                    print("Schedule not known")

    def _send_value(self, ip, urlsuffix):
        try:
            response = urllib.request.urlopen(f'http://{ip}/{urlsuffix}').read().decode('utf-8')
        except:
            logging.info('Value could not be set, sorry!')

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

    def updateallvalues(self, ip):
        """
        Update the boiler data
        """
        self._scan_device(ip)

    def updateschedules(self, ip):
        """
        Update the schedule data
        """
        self._weekly_schedule(ip)

    def boostonoff(self, ip, boost):
        """
        Turn on or off the boost.
        URL example: http://192.168.2.254/boostSW?mode=0
        ---
        Send off value: boiler.boostonoff("192.168.2.254", 0)
        Send on value: boiler.boostonoff("192.168.2.254", 1)
        Note:
        You need atleast a few seccond between request, else the boiler might
        not switch thesse this can be fixed with turning the boiler on and off.
        """
        if isinstance(boost, int):
            allowedvalues = [0, 1]
            if boost in allowedvalues:
                urlsuffix = f"boostSW?mode={boost}"
                self._send_value(ip, urlsuffix)
            else:
                logging.info('Parameter given for boost must be either 0 or 1, you supplied: %s', boost)
        else:
            logging.info('Parameter given must be a valid number (1 or 0)')

    def boileronoff(self, ip, power):
        """
        Turn on or off the boiler itself.
        URL example: http://192.168.2.254/power?val=on
        ---
        Send off value: boiler.boileronoff("192.168.2.254","off")
        Send on value: boiler.boileronoff("192.168.2.254","on")
        """
        allowedvalues = ["on", "off"]
        if power in allowedvalues:
            urlsuffix = f"power?val={power}"
            self._send_value(ip, urlsuffix)
        else:
            logging.info('Parameter given for power must be either "on" or "off", you supplied: %s', power)

    def boilermode(self, ip, mode):
        """
        Turn on or off manual temperature override.
        URL example: http://192.168.2.254/modeSW?mode=1
        ---
        Send off value: boiler.boilermanualmode("192.168.2.254", 0)
        Send on value: boiler.boilermanualmode("192.168.2.254", 1)
        """
        if isinstance(mode, int):
            if 0 <= mode < 9:
                urlsuffix = f"modeSW?mode={mode}"
                self._send_value(ip, urlsuffix)
            else:
                logging.info('Parameter given to mode mode can be 0 up to 9, you supplied: %s', mode)
        else:
            logging.info('Parameter given must be a valid number 0 up up to 9')

    def manualtemp(self, ip, temp):
        """
        Set manual temperature.
        URL example: http://192.168.2.254/setTemp?val=45
        ---
        Send value: boiler.manualtemp("192.168.2.254", 45)
        Must be between 14 and 75, note that manual mode must be on.
        """
        if isinstance(temp, int):
            if 14 < temp < 75:
                urlsuffix = f"setTemp?val={temp}"
                self._send_value(ip, urlsuffix)
            else:
                logging.info('Parameter given to manual temp must be a number between 14 and 75')
        else:
            logging.info('Parameter given to manual temp must be a valid number EG 45 and not 45.00')

    def automanualtemp(self, ip, temp):
        """
        Turn on manual temperature override.
        And set a temperature this guarantees a correct order of operations
        """
        # ToDo, check if it is needed
        self.boilermanualmode(ip, 1)
        self.manualtemp(ip, temp)

    def resetpower(self, ip):
        """
        This resets the energy consumption:
        > Power consumption from the moment of the of the reset
        Note: this is not the total consumption since you turned on the device.
        """
        urlsuffix = f"resetPow"
        self._send_value(ip, urlsuffix)

    def settime(self, ip, tz):
        """
        Set time and date to now on the boiler
        This needs a time zone like Europe/Amsterdam
        EG: boiler.settime("192.168.2.254", "Europe/Amsterdam")
        This relies on the boiler supplying the data :/
        """
        today = datetime.datetime.today()
        if os.name == "posix":
            day = today.strftime("%-d")
        else:
            # This is for windows
            day = today.strftime("%#d")
        sec = today.strftime("%S")
        min = today.strftime("%M")
        hour = today.strftime("%H")
        month = today.strftime("%m")
        year = today.strftime("%Y")
        zoneurl = f"http://{ip}/langs/en-US.json"
        response = json.loads(urllib.request.urlopen(zoneurl, timeout=urltimeout).read().decode())
        selected_tz = response['cityTimeZoneOption'][tz]['value']
        urlsuffix = f"setdate?tOffset={selected_tz}&tDay={day}&tMonth={month}&tYear={year}&tHour={hour}&tMin={min}&tSec={sec}"
        self._send_value(ip, urlsuffix)

    # SetVacation
    # SetPower
    #

if __name__ == "__main__":
    tesy = tesy()
