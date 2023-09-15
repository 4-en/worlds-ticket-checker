# checks for available tickets for lol worlds 2023

import requests
import time

ENABLE_WINDOWS_NOTIFICATIONS = True

#check if os is windows
import os
if os.name != "nt":
    ENABLE_WINDOWS_NOTIFICATIONS = False
    print("Windows notifications are not enabled because you are not on Windows")

if ENABLE_WINDOWS_NOTIFICATIONS:
    from windows_toasts import Toast, WindowsToaster


class Checker:
    """
    Checks for available tickets for lol worlds 2023"""
    def __init__(self):
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
        
        # add available tickets on thursday for testing
        self.urls.append("https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009639&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001")
        
        # create toaster if enabled
        if ENABLE_WINDOWS_NOTIFICATIONS:
            self.toaster = WindowsToaster("Worlds 2023 Tickets")
        
    def checkLoop(self, interval=60):
        """Checks for tickets every interval seconds"""
        count = 0
        try:
            while True:
                self.checkAll()

                count += 1
                print("Checked " + str(count) + " times", end="\r")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            print("Exiting...")
            exit(0)
    
    def checkAll(self):
        """Checks all urls"""
        for url in self.urls:
            self.check(url)


    def on_available(self, site_url):
        """Called when tickets are available.
        Useful to override for custom notifications"""

        # send windows notification if enabled
        if ENABLE_WINDOWS_NOTIFICATIONS:
            # show notification
            toast = Toast(("Tickets are available", "Click to open website", site_url))
            toast.on_activated = lambda _: os.startfile(site_url)
            self.toaster.show_toast(toast)

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

            # print total count
            
            if totalCount > 0:
                print()
                print("Tickets are available")

                # print link to website
                goodsCode = url[url.find("GoodsCode=")+10:url.find("&PlaceCode")]
                if goodsCode == "23010160":
                    print("FINAL TICKETS ARE AVAILABLE@@@@")
                print(self.link.format(GoodsCode=goodsCode))

                # call on_available
                self.on_available(self.link.format(GoodsCode=goodsCode))


        else:
            # print error message
            print()
            print("Error: Could not connect to website")
            print("Status Code: " + str(response.status_code))
        

def main():
    checker = Checker()
    checker.checkLoop()

if __name__ == "__main__":
    main()