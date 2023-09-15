# checks for available tickets for lol worlds 2023

import requests
import time


class Checker:
    def __init__(self):
        self.link = "https://www.globalinterpark.com/product/{GoodsCode}?lang=en"
        self.urls = ["https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23010160&PlaceCode=23000829&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009641&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009337&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009336&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009640&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009338&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009642&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001",
            "https://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=23009339&PlaceCode=23000822&PlaySeq=001&LanguageType=G2001"]
        
    def checkLoop(self, interval=60):
        count = 0
        while True:
            self.checkAll()
            count += 1
            print("Checked " + str(count) + " times", end="\r")
            time.sleep(interval)
    
    def checkAll(self):
        for url in self.urls:
            self.check(url)

    def check(self, url):
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