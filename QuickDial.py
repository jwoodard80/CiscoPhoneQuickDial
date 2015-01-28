__author__ = 'jwoodard'

# TODO -- Possibly display the last 5 numbers dialed and make them redialed with A-E options
# TODO -- Encrypt FAC and Password
# TODO -- DONE --First run prompt for creds and FAC, store creds to an encrypted file
# TODO -- DONE -- Take Input "ld918704036566" ld and change to 918704036566,FAC#
# todo -- DONE -- if input longer than 4 digits, append 9
# todo -- DONE -- if longer than 6 digts append 91
# todo -- DONE -- Must be numbers length 4,7 or 10 and optionally 'f'
# todo -- DONE -- Note 10 digit number lacking 'f' and prompt for adding FAC

import requests
import getpass
from requests.auth import HTTPBasicAuth
import ConfigParser

def setupconfig():
    setup = ConfigParser.SafeConfigParser()
    setup.add_section("Information")
    setup.set('Information', 'user', raw_input("Please enter your username: "))
    setup.set('Information', 'password', raw_input("Please enter your password: "))
    setup.set('Information', 'fac', raw_input("Please enter your FAC Code: "))
    setup.set('Information', 'phone', raw_input("Enter your phone device name: "))
    setup.set('Information', 'ip', raw_input("Enter your phone IP address: "))

    print"Writing config file...."

    with open("C:\\Users\\jwoodard\\CiscoPhoneQuickDial\\QuickDialConfig.ini", 'w') as configfile:
        setup.write(configfile)
    print "Done"
    return True


def configcheck(): # If config is not set, ask setup questions and create file
    test = False

    while not test: # fails if no file, creates file and sets while test to true allowing
        try:
            ini_file = open("C:\\Users\\jwoodard\\CiscoPhoneQuickDial\\QuickDialConfig.ini")
            test = True
        except IOError:
            print "Error: Could not find config file... Running setup.\n\n"
            setupconfig()

    parser = ConfigParser.ConfigParser()
    parser.readfp(ini_file)
    return parser


def addFAC(x):
    x = x + ','+parser.get("Information", "fac")+'#'
    return x


def oopsfac(x):
    if len(x) == 10 and ('f' not in x):
        test = raw_input("I noticed you didn't put a FAC in, would you like to? (Y/N)")
        if test == 'y':
            x = addFAC(x)
        return x


def prompt():
    print "Quick Favorites"
    #for shortcut, call in parser.items('RecentCalls'):
    #    print "({0}) = {1}".format(shortcut, call)

    NumberToDial = raw_input("Enter (a-e) or number to dial: ")
    return NumberToDial


def formatdial(input_numbers): ##8704036566
    
    fac = False
    
    if str("f") in input_numbers:
        input_numbers = input_numbers.replace("f", '')
        fac = True

    if len(input_numbers) == 4:
        input_numbers = input_numbers
        
    elif len(input_numbers) == 7:
        # noinspection PyAugmentAssignment
        input_numbers = '9' + input_numbers
    elif len(input_numbers) == 10:
        ## FAC Check

        if not fac: 
            input_numbers = oopsfac(input_numbers)
        else:
            input_numbers = addFAC(input_numbers)

        # noinspection PyAugmentAssignment
        input_numbers = '91' + input_numbers
    else:
        print "DIGIT ERROR: " + str(len(input_numbers)) + ' digits given. Only length 4,7 or 10 accepted. '
        input_numbers = False

    return input_numbers


def dialNumbers(number):
    xml = 'XML=' + '<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="Dial:' + number + '"/></CiscoIPPhoneExecute>'

    headers = {
        'Host': parser.get("Information", "ip"),  # TODO -- Find this IP Automatically
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print 'Calling: ' + number

    try:
        r = requests.post('http://'+parser.get("Information", "ip")+'/CGI/Execute',
                          data=xml,
                          headers=headers,
                          auth=HTTPBasicAuth(parser.get("Information", "User"), parser.get("Information", "password")))

    except requests.ConnectionError, e:
        print e

parser = configcheck()
dial = False

while dial is False:
    dial = formatdial(prompt())
    print dial
    dialNumbers(dial)