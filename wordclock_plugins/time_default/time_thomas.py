import datetime as dt

class time_thomas():
    '''
    This class returns a given time as a range of LED-indices.
    Illuminating these LEDs represents the current time on a german WCA
    '''

    def __init__(self):
        # ES IST
        self.prefix = range(0,2) + range(3,6)
        self.minutes=[[], \
            # FUENF NACH
            range(7,11) + range(40,44), \
            # ZEHN NACH
            range(11,15) + range(40,44), \
            # VIERTEL NACH
            range(26,33) + range(40,44), \
            # ZWANZIG NACH
            range(15,22) + range(40,44), \
            # FUENF VOR HALB
            range(7,11) + range(33,36) + range(44,48), \
            # HALB
            range(44,48), \
            # FUENF NACH HALB
            range(7,11) + range(40,44) + range(44,48), \
            # ZWANZIG VOR
            range(15,22) + range(33,36), \
            # VIERTEL VOR
            range(26,33) + range(33,36), \
            # ZEHN VOR
            range(11,15) + range(33,36), \
            # FUENF VOR
            range(7,11) + range(33,36) ]
            # ZWOELF
        self.hours= [range(94,99), \
            # EINS
            range(55,59), \
            # ZWEI
            range(62,66), \
            # DREI
            range(66,70), \
            # VIER
            range(73,77), \
            # FUENF
            range(51,55), \
            # SECHS
            range(77,82), \
            # SIEBEN
            range(88,94), \
            # ACHT
            range(84,88), \
            # NEUN
            range(102,106), \
            # ZEHN
            range(99,103), \
            # ELF
            range(49,52), \
            # ZWOELF
            range(94,99)]
            # UHR
        self.full_hour= range(107,110)

    def get_time(self, time, withPrefix=True):
        hour=time.hour%12+(1 if time.minute/5 > 4 else 0)
        minute=time.minute/5
        # Assemble indices
        return  \
            (self.prefix if withPrefix else []) + \
            self.minutes[minute] + \
            self.hours[hour] + \
            ([60] if (hour == 1 and minute != 0) else []) + \
            (self.full_hour if (minute == 0) else [])

