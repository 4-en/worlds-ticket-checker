# checks for available tickets for lol worlds 2023

import requests
import time
import smtplib, ssl
import random
import os
import xml.etree.ElementTree as ET


def xml_to_dict(element):
    result = {}
    for child in element:
        child_dict = xml_to_dict(child)
        if child_dict:
            if child.tag in result:
                if type(result[child.tag]) is list:
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict
        elif child.text:
            result[child.tag] = child.text
    return result

def xml_string_to_dict(xml: str):
    root = ET.fromstring(xml)
    return xml_to_dict(root)

class Checker:
    """
    Checks for available tickets for lol worlds 2023
    Base class with cmd line output in on_available
    """
    def __init__(self, urls=None, interval=10, randomize=False):
        # link to buy tickets
        self.link = "https://www.globalinterpark.com/product/{GoodsCode}?lang=en"

        # list of urls to check
        # only links for weekend swiss rounds and finals
        self.urls = ["https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23010160&PlaceCode=23000829&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009641&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009337&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009336&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009640&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009338&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009642&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009339&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001"]
        
        # use provided urls if not None
        if urls is not None:
            self.urls = urls

        self.notifiedTracker = set()

        self.interval = interval
        self.randomize = randomize
        self.finalsOnly = True

    def getSleepTime(self):
        """Returns time to sleep before checking again"""
        if not self.randomize:
            return self.interval
        
        # randomize sleep time
        rand = random.random() ** 2 * self.interval
        rand = rand if random.random() < 0.5 else -rand
        sleepTime = max(1,self.interval + rand)
        return sleepTime

        
    def checkLoop(self):
        """Checks for tickets every self.interval seconds"""
        count = 0
        try:
            print("[{}] Checking for tickets every ".format(time.strftime("%H:%M:%S")) + ("~" if self.randomize else "") + str(self.interval) + " seconds")
            while True:
                self.checkAll()

                count += 1
                print("Checked " + str(count) + " times", end="\r")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            print("Exiting...")
            exit(0)
    
    def checkAll(self):
        """Checks all urls"""
        for url in self.urls:
            if self.finalsOnly:
                if not "23010160" in url:
                    continue
            self.check(url)


    def on_available(self, message, site_url):
        """Called when tickets are available.
        Useful to override for custom notifications"""

        print(message)
        print(site_url)


    def on_unavailable(self, message):
        """Called when tickets are unavailable.
        Useful to override for custom notifications"""

        print(message)
        

    def check(self, url):
        """Checks url for tickets
        Prints message if tickets are available"""
        # make request to url
        response = requests.get(url)
        # check if response is good
        if response.status_code == 200:
            # check if there are tickets available
            # find <RemainCnt>COUNT</RemainCnt>
            totalCount = 0
            index = 0

            d = xml_string_to_dict(response.text)
            tickets = {}
            for i in d["Table"]:
                available = int(i["RemainCnt"])
                if available > 0:
                    name = i["SeatGradeName"]
                    # remove non ascii characters
                    name = "".join([c for c in name if ord(c) < 128])
                    tickets[name] = available


            
            if len(tickets) > 0:
                # tickets are available

                # check if already notified
                if url in self.notifiedTracker:
                    return
                
                # add to notified tracker
                self.notifiedTracker.add(url)

                msg = "[{}] Tickets are available".format(time.strftime("%H:%M:%S"))

                # print link to website
                goodsCode = url[url.find("GoodsCode=")+10:url.find("&PlaceCode")]
                if goodsCode == "23010160":
                    msg = "[{}] @@@@ FINAL TICKETS ARE AVAILABLE @@@@@".format(time.strftime("%H:%M:%S"))
                
                
                msg += "\n" + "\n".join([k + ": " + str(v) for k,v in tickets.items()])
                
                link = self.link.format(GoodsCode=goodsCode)

                # call on_available
                self.on_available(msg, link)

            else:
                # tickets are not available
                # remove from notified tracker
                if url in self.notifiedTracker:
                    self.notifiedTracker.remove(url)

                    # tickets no longer available
                    msg = "[{}] Tickets are no longer available".format(time.strftime("%H:%M:%S"))
                    # call on_unavailable
                    self.on_unavailable(msg)



        else:
            # print error message
            print()
            print("Error: Could not connect to website")
            print("Status Code: " + str(response.status_code))


class AdvancedChecker(Checker):
    """
    Checker with email and windows notifications
    """

    def __init__(self, urls=None, interval=10, randomize=False, port=465, smtp_server="smtp.gmail.com", receiver_email=None, user=None, password=None):
        super().__init__(urls, interval, randomize)

        # check if platform is windows
        if os.name == "nt":
            #import toaster
            from windows_toasts import Toast, WindowsToaster
            self.Toast = Toast
            self.WindowsToaster = WindowsToaster

            self.toaster = self.WindowsToaster("Worlds 2023 Tickets")
        else:
            self.toaster = None

        # load user and password from file
        self.emailLoaded = False
        self.smtp_server = smtp_server
        self.port = port
        self.USER = user
        self.PASSWORD = password
        self.RECEIVER_EMAIL = receiver_email

        if self.USER is not None and self.PASSWORD is not None and self.RECEIVER_EMAIL is not None:
            self.emailLoaded = True
        else:
            try:
                with open("email.cfg", "r") as file:
                    self.USER = file.readline().strip()
                    self.PASSWORD = file.readline().strip()
                    self.RECEIVER_EMAIL = file.readline().strip()
            except FileNotFoundError:
                print("email.cfg not found. Please create it with the following format:")
                print("user")
                print("password")
                print("receiver email")
                print("Continuing without email notifications")
            else:
                print("Loaded user and password from email.cfg")
                self.emailLoaded = True

        # send start email
        self.send_email("Ticket checker is running", "You will receive an email when tickets are available")
        

    def send_email(self, subject="", message=""):
        """Sends email to RECEIVER_EMAIL with message"""
        if not self.emailLoaded:
            return

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.USER, self.PASSWORD)
            server.sendmail(self.USER, self.RECEIVER_EMAIL, "Subject: " + subject + "\n\n" + message)

    def on_available(self, message, site_url):
        """Called when tickets are available.
        Useful to override for custom notifications"""

        super().on_available(message, site_url)

        # send email
        self.send_email("Tickets are available", message + "\n" + site_url)

        # send windows notification
        if self.toaster is not None:
            toast = self.Toast((message, "Click to open website", site_url))
            toast.on_activated = lambda _: os.startfile(site_url)
            self.toaster.show_toast(toast)
        

def main():
    # if called from command line, import argparse
    import argparse

    # parse arguments
    parser = argparse.ArgumentParser(description="Checks for available tickets for lol worlds 2023")
    parser.add_argument("-i", "--interval", type=int, default=10, help="Interval in seconds between checks")
    parser.add_argument("-b", "--basic", action="store_true", help="Use basic checker")
    parser.add_argument("-u", "--user", type=str, help="User for email notifications")
    parser.add_argument("-p", "--password", type=str, help="Password for email notifications")
    parser.add_argument("-r", "--receiver", type=str, help="Receiver email for email notifications")
    parser.add_argument("-s", "--server", type=str, default="smtp.gmail.com", help="SMTP server for email notifications")


    # create checker
    checker = AdvancedChecker(
        interval=parser.parse_args().interval,
        randomize=True,
        user=parser.parse_args().user,
        password=parser.parse_args().password,
        receiver_email=parser.parse_args().receiver,
        smtp_server=parser.parse_args().server
    ) if not parser.parse_args().basic else Checker(
        interval=parser.parse_args().interval,
        randomize=True
    )
    checker.checkLoop()

if __name__ == "__main__":
    main()