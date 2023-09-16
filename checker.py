# checks for available tickets for lol worlds 2023

import requests
import time
import smtplib, ssl
import random
import os


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
            self.check(url)


    def on_available(self, message, site_url):
        """Called when tickets are available.
        Useful to override for custom notifications"""

        print(message)
        print(site_url)

        

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
            while index < len(response.text):
                index = response.text.find("<RemainCnt>", index)
                if index == -1:
                    break
                end = response.text.find("</RemainCnt>", index)
                totalCount += int(response.text[index + 11:end])
                index = end+1

            
            if totalCount > 0:
                # tickets are available

                # check if already notified
                if url in self.notifiedTracker:
                    return

                msg = "Tickets are available"

                # print link to website
                goodsCode = url[url.find("GoodsCode=")+10:url.find("&PlaceCode")]
                if goodsCode == "23010160":
                    msg = "FINAL TICKETS ARE AVAILABLE@@@@"
                
                link = self.link.format(GoodsCode=goodsCode)

                # call on_available
                self.on_available(msg, link)

            else:
                # tickets are not available
                # remove from notified tracker
                if url in self.notifiedTracker:
                    self.notifiedTracker.remove(url)


        else:
            # print error message
            print()
            print("Error: Could not connect to website")
            print("Status Code: " + str(response.status_code))


class AdvancedChecker(Checker):
    """
    Checker with email and windows notifications
    """

    def __init__(self, urls=None, interval=10, randomize=False, port=465, smtp_server="smtp.gmail.com"):
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
    checker = AdvancedChecker(interval=10, randomize=True)
    checker.checkLoop()

if __name__ == "__main__":
    main()