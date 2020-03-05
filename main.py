#!/usr/bin/env python
# encoding: utf-8
#
# hUEY
# cde admin info scraper

import time
import csv
import random
import requests
import urllib.request
from bs4 import BeautifulSoup

url = 'https://www.cde.ca.gov/SchoolDirectory/details?cdscode='
info_url_1 = 'https://www.cde.ca.gov/sdprofile/details.aspx?cds='
info_url_2 = 'https://dq.cde.ca.gov/dataquest/dqcensus/enrethlevels.aspx?agglevel=School&year=2018-19&cds='
query_sleep_time = 0.1

test_0 = "01611766134084"
test_1 = "43694684331799"
test_2 = "43694196046940"
test_3 = "01612916002414"

def scrapeAllInfo():
    result = ""

    page = requests.get(url + test_1)
    soup = BeautifulSoup(page.text, 'html.parser')
    div = soup.find('th', text="Administrator").find_next_sibling().find('div')

    current = div.next_element
    while current.name != "a":
        if current.name != "br":
            text = current.strip()
            if text != "":
                result = result + text + ","
        current = current.next_element

    result += current.text

    return result

def main():
    listOfCodes = []

    print()
    print("Hi Shy!")
    print()
    print("Input 'file' to read in a batch of codes")
    print("Input 'manual' to analyze your own codes")
    mode = input(" > ")
    print()

    if mode == "file":
        print("Input file name, with extension")
        filename = input(" > ")
        f = open(filename, 'r')
        count = 0

        print()
        print("Reading...")
        while True:
            count += 1
            line = f.readline().strip()

            if not line:
                break

            listOfCodes.append(line)
            print("Code {}: {}".format(count, line))

        f.close()
        print("File successfully read")

        print()
        print("Initialize scrape? (Y/N)")
        proceed = input(" > ")
        if proceed != "Y" and proceed != "y":
            print("Exiting!")
            return
        print()

    elif mode == "manual":
        print("Manual commands:")
        print("Enter 'list' to see inputted codes.")
        print("Enter 'remove' to enter remove mode.")
        print("Enter 'done' to start scraping.")
        print("Enter 'exit' to stop the program (will lose input).")
        print()

        print("To use, input CDS codes followed by enter.")

        while True:
            code = input(" > ")

            if code == "":
                continue

            if code == "exit":
                print("Exiting!")
                return

            elif code == "done":
                break

            elif code == "list":
                print()
                print("Current codes:")
                for x in range(len(listOfCodes)):
                    print(str(x) + ": " + str(listOfCodes[x]))
                print()

            elif code == "remove":
                while True:
                    print("Here is the current list of codes:")
                    for x in range(len(listOfCodes)):
                        print(str(x) + ": " + str(listOfCodes[x]))
                    print("Input the index to remove or 'done':")

                    toRemove = input(" > ")
                    if toRemove == "done":
                        print("Back to input:")
                        break
                    else:
                        listOfCodes.pop(int(toRemove))

            else:
                listOfCodes.append(code)
                print("Got it!")

            print()

    elif mode == "exit":
        print("Exiting!")
        return

    else:
        print("Did not recognize that command.")
        print("Exiting!")
        return

    queries(listOfCodes)

def queries(codes):
    print("Systems firing!")
    adminInfo = []

    for x in range(len(codes)):
        info = getSchoolInfoByCode(codes[x])
        adminInfo.append([codes[x], info[0], info[1], info[2], info[3]])
        # Sleep to avoid spamming their server
        time.sleep(query_sleep_time)
        print(x)

    for x in range(len(adminInfo)):
        print(adminInfo[x])
    print()

    writeInfoCSV(adminInfo)

def getSchoolInfoByCode(code):
    page = requests.get(info_url_1 + code)
    # if page is None:
    #     return "Invalid code"
    soup = BeautifulSoup(page.text, 'html.parser')

    el = soup.find(id='lblEnglishLanguageLearners').text
    el_learners = el[el.find("(")+1:el.find("%")-1]
    fl = soup.find(id='lblFreeLunch').text
    free_lunch = fl[fl.find("(")+1:fl.find("%")-1]

    page = requests.get(info_url_2 + code)
    soup = BeautifulSoup(page.text, 'html.parser')
    tab = soup.find('td', class_='total').next_sibling
    af_amer = tab.text[:-1]
    as_amer = tab.next_sibling.next_sibling.text[:-1]

    return [el_learners, free_lunch, af_amer, as_amer]


def getAdminInfoByCode(code):
    page = requests.get(url + code)
    if page is None:
        return "Invalid code"

    soup = BeautifulSoup(page.text, 'html.parser')
    target = soup.find('th', text="Administrator")
    if target is None:
        return ["No Info", "N/A"]

    div = target.find_next_sibling().find('div')
    name = div.next_element.strip()
    link = div.find('a')
    email = "N/A" if link is None else link.text.strip()

    return [name, email]

def writeCSV(output):
    print("Input desired output filename. Must have '.csv' extension.")
    print("Defaults to 'output.csv' if blank!")
    inputName = input(" > ")

    if inputName == "exit":
        print("Exiting!")
        return

    outputFile = inputName if inputName != "" else "output.csv"

    with open(outputFile, mode='w') as admin_file:
        admin_writer = csv.writer(admin_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        admin_writer.writerow(["CDS Code", "Administrator", "Email"])
        for x in range(len(output)):
            admin_writer.writerow(output[x])

    print()
    print("File written! Goodbye!")

def writeInfoCSV(output):
    print("Input desired output filename. Must have '.csv' extension.")
    print("Defaults to 'output.csv' if blank!")
    inputName = input(" > ")

    if inputName == "exit":
        print("Exiting!")
        return

    outputFile = inputName if inputName != "" else "output.csv"

    with open(outputFile, mode='w') as admin_file:
        admin_writer = csv.writer(admin_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        admin_writer.writerow(["CDS Code", "English Language Learners '%'", "Free/Reduced Lunch '%'", "African American '%'", "Asian '%'"])
        for x in range(len(output)):
            admin_writer.writerow(output[x])

    print()
    print("File written! Goodbye!")

if __name__ == "__main__":
    main()