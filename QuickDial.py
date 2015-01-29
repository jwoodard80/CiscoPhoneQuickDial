__author__ = 'jwoodard'


# TODO -- Find phone IP Automatically
# TODO -- DONE -- Create Folder for ini file
# TODO -- Check for any unauthorized response
# TODO -- DONE -- Operating system check for ini_location
# TODO -- DONE -- First run prompt for creds and FAC
# TODO -- DONE -- Store creds to an encrypted file
# TODO -- DONE -- Take Input "ld918704036566" ld and change to 918704036566,FAC#
# todo -- DONE -- if input longer than 4 digits, append 9
# todo -- DONE -- if longer than 6 digts append 91
# todo -- DONE -- Must be numbers length 4,7 or 10 and optionally 'f'
# todo -- DONE -- Note 10 digit number lacking 'f' and prompt for adding FAC

import requests
import getpass
import platform  # may not need this since we have to have os
import os
import re
from requests.auth import HTTPBasicAuth
import ConfigParser
import base64


def encode(secretkey, clear):
    enc = []
    for i in range(len(clear)):
        key_c = secretkey[i % len(secretkey)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))


def decode(secretkey, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = secretkey[i % len(secretkey)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def os_check():
    locations = {
        "Windows": "C:\\Users\\" + getpass.getuser() + "\\CiscoPhoneQuickDial\\",
        "Linux": "\\home\\USER\\.config\\QuickDialConfig\\QuickDialConfig.ini",
        "Darwin": "Some OSX Location"
    }
    ini = locations[platform.system()]
    return ini


def setupconfig():
    print "---Quick Dial Setup---"
    setup = ConfigParser.SafeConfigParser()
    setup.add_section("Information")
    setup.set('Information', 'user', raw_input("Please enter your username: "))
    setup.set('Information', 'password', encode(key, getpass.getpass("Please enter your password: ")))
    setup.set('Information', 'fac', encode(key, raw_input("Please enter your FAC Code: ")))
    setup.set('Information', 'phone', raw_input("Enter your phone device name: "))
    setup.set('Information', 'ip', raw_input("Enter your phone IP address: "))
    print "\n"

    count = 0
    while count != 2:
        if os.path.exists(ini_location):
            print "OK"
            count = 2
        else:
            print "Config folder not found, attempting to create...."
            os.makedirs(ini_location)
            count = 1

        print"Folder Found! Attempting to write config file...."
        try:
            with open(ini_location + ini_file, 'w') as configfile:
                setup.write(configfile)
                print "Success!!"
                return True
        except IOError:
            print "ERROR: Unable to create file. Check write permissions to location"
            print "Expected Location: " + ini_location + ini_file
            raise SystemExit()


def configcheck():  # If config is not set, ask setup questions and create file
    test = False

    while not test:  # fails if no file, creates file and sets while test to true allowing
        try:
            full_file = open(ini_location + ini_file)
            test = True
        except IOError:
            print "Could not find config file... Attempting initial setup.\n"
            setupconfig()

    parser = ConfigParser.ConfigParser()
    parser.readfp(full_file)
    return parser


def addFAC(x):
    x = x + ',' + decode(key, parser.get("Information", "fac")) + '#'
    return x


def oopsfac(x):
    if len(x) == 10 and ('f' not in x):
        test = raw_input("I noticed you didn't put a FAC in, would you like to? (Y/N)")
        if test == 'y':
            x = addFAC(x)
        return x


def prompt():
    NumberToDial = raw_input("Enter number to dial: ")
    return NumberToDial


def validcheck(input):
    pattern = '^[0-9f]*$'
    match = re.search(pattern, input)
    if match:
        answer = True
    else:
        answer = False
    return answer

def formatdial(input_numbers):

    if not validcheck(input_numbers):
        print "INPUT ERROR: Only number string of 4,7 or 10 digits and 'f' accepted. "
        return False

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
    xml = 'XML=<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="Dial:' + number + '"/></CiscoIPPhoneExecute>'

    headers = {
        'Host': parser.get("Information", "ip"),
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    print 'Attempting to call: ' + number + '....'
    try:
        requests.post('http://' + parser.get("Information", "ip") + '/CGI/Execute',
                      data=xml,
                      headers=headers,
                      auth=HTTPBasicAuth(parser.get("Information", "User"),
                                         decode(key, parser.get("Information", "password"))))

    except requests.ConnectionError, e:
        print e


print "****Cisco Quick Dial****"
ini_file = "QuickDialConfig.ini"  # File to append to folder
ini_location = os_check()  # Folder Location
key = "tu82BZQAp9Zdhe=#EbwYGRPUCmveQ^D$cE$8u#mKZv5yUE%d2r5A*!v5HchE?vxdq&thDQHbsRmnHNEMj5kAWDsV^a3qD3?_B"

parser = configcheck()
dial = False

while dial is False:
    dial = formatdial(prompt())

dialNumbers(dial)