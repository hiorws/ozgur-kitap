#!/usr/bin/env python

__author__ = "Ozgur Firat Cinar"

import xlsxwriter
from BeautifulSoup import BeautifulSoup
import time
from mechanize import Browser
import datetime
import re


class BookStore():
    EMEK_E_MAIL = ''
    EMEK_PASSWORD = ''

    def __init__(self):
        try:
            login_credentials = open("emek-kullanici-bilgileri.txt", "r")
            list_credentials = login_credentials.readlines()
            username_cr_list = list_credentials[0].split("EMEK_KITAP_KULLANICI_ADI = ")[1]
            password_cr_list = list_credentials[1].split("EMEK_KITAP_SIFRE = ")[1]
            emek_username = username_cr_list.replace('"', '')
            emek_password = password_cr_list.replace('"', '')

            self.EMEK_E_MAIL = emek_username
            self.EMEK_PASSWORD = emek_password
        except IOError:
            print "Lutfen emek-kullanici-bilgileri.txt dosyasini olusturunuz."
            emek_username = raw_input("Emek Kitap e-mail adresini giriniz:")
            emek_password = raw_input("Emek Kitap sifrenizi adresini giriniz:")

            self.EMEK_E_MAIL = emek_username
            self.EMEK_PASSWORD = emek_password
        except:
            emek_username = raw_input("Emek Kitap e-mail adresini giriniz:")
            emek_password = raw_input("Emek Kitap sifrenizi adresini giriniz:")

            self.EMEK_E_MAIL = emek_username
            self.EMEK_PASSWORD = emek_password

    def main(self):
        """
            main definition
        """

        entered_file_name = raw_input(
            "Kaydedilecek dosya adi girin: (bos birakirsaniz tarih/saat seklinde kaydedilecek)\n")

        if entered_file_name == "":
            i = datetime.datetime.now()
            day = str(i.day) + "_" + str(i.month) + "_" + str(i.year)
            clock = str(i.hour) + "-" + str(i.minute) + "-" + str(i.second)
            date_file_name = day + "_" + clock
            print "Kaydedilecek dosya adi: " + date_file_name + "\n"
            file_name = date_file_name
            wb = xlsxwriter.Workbook(date_file_name + ".xlsx")
        else:
            file_name = entered_file_name
            wb = xlsxwriter.Workbook(entered_file_name + ".xlsx")

        ws = self.set_xls_layout(wb)

        counter = 2
        barcode_column = "A"
        count_column = "E"
        book_column = "B"
        author_column = "C"
        publisher_column = "D"
        price_column = "F"
        discount_column = "G"

        while True:

            entry = raw_input("\n\n\n\n\n\n\n\n\n\nYeni Barkod Tara: \n")
            print "Kitap bilgileri getiriliyor."

            if entry == "e":
                wb.close()
                print "Dosya basariyla kaydedildi."
                print "Kaydedilen dosya adi: " + file_name
                exit()
            else:
                try:
                    book_dict = self.book_shop_login(entry)
                    if 'book_name' and 'author_name' and 'publisher_name' and 'price' and 'discount' in book_dict.keys():
                        book = book_dict['book_name']
                        author = book_dict['author_name']
                        publishing_house = book_dict['publisher_name']
                        price = book_dict['price']
                        discount = book_dict['discount']
                        ws.write(str(barcode_column) + str(counter), entry)
                        ws.write(str(book_column) + str(counter), book)
                        ws.write(str(author_column) + str(counter), author)
                        ws.write(str(publisher_column) + str(counter), publishing_house)
                        ws.write(str(count_column) + str(counter), 1)
                        ws.write(str(price_column) + str(counter), price)
                        ws.write(str(discount_column) + str(counter), discount)
                        print "Girilen kitap sayisi %s" % str(counter - 1)
                    else:
                        ws.write(str(barcode_column) + str(counter), entry)
                        print "Girilen kitap sayisi %s" % str(counter - 1)
                    counter += 1
                except AttributeError:
                    print "Yanlis barkod."
                    print "==============\n"

    def set_xls_layout(self, workbook):
        worksheet = workbook.add_worksheet()

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 10)

        worksheet.write("A1", "Barkod Numarasi")
        worksheet.write("B1", "Kitap Adi")
        worksheet.write("C1", "Yazar Adi")
        worksheet.write("D1", "Yayinevi")
        worksheet.write("E1", "Adet")
        worksheet.write("F1", "Satis Fiyati")
        worksheet.write("G1", "Iskonto")

        return worksheet

    def clear_screen(self):
        for i in range(1, 50):
            print "\n"

    def book_shop_login(self, barcode):
        """
            login www.emekkitap.com
        """

        login_page = "https://www.emekkitap.com/Account/LogOn"
        main_search_page = "http://www.emekkitap.com/Search?q="
        search_page_link = main_search_page + barcode

        br = Browser()

        br.set_handle_robots(False)
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        # br.set_handle_gzip(True)
        # br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        br.open(login_page)
        br.select_form(nr=1)
        br['EmailAddress'] = self.EMEK_E_MAIL
        br['Password'] = self.EMEK_PASSWORD
        logged_in = br.submit()
        logged_in.read()
        # logincheck = logged_in.read()

        br.open(search_page_link)
        print "Lutfen bekleyiniz...\n"
        time.sleep(0.5)
        htmlstring = br.response().read()
        try:
            soup = BeautifulSoup(htmlstring)
            price_div = soup.find("div", {"class": "liste-sepet"})
            price_text = price_div.contents[1]
            price = re.findall('\d+,\d+', price_text.text)[0]

            discount_div = soup.find("p", {"class": "urun-indirim"})
            discount_text = discount_div.contents[0]
            discount = discount_text.split(": %")[1]

            book_div = soup.find("p", {"class": "urun-ismi"})
            book_long_text = book_div.contents[1]
            book_name = book_long_text.text

            author = soup.find("p", {"class": "urun-yazar"})
            author_long_text = author.contents[0]
            author_name = author_long_text.text

            publisher = ''
            for a in soup.findAll('a'):
                if 'brand/product' in a['href']:
                    publisher = a.text

            self.clear_screen()
            print "=============="
            print "Kitap Adi: " + book_name
            print "Yazar Adi: " + author_name
            print "Yayinevi: " + publisher
            print "Fiyat: " + price
            print "Iskonto: " + discount
            print "=============="

            return {'book_name': book_name, 'author_name': author_name, 'publisher_name': publisher, 'price': price,
                    'discount': discount}

        except:
            print "Emek Kitap veritabaninda bu barkod numarali kitap bulunamadi."
            return {'barcode': barcode}

            # return book_name, author_name, publisher, price, discount


def print_ascii():
    print """
     ____                                       _
     |  _ \ _   _ ______ _  __ _ _ __ __ _ _   _| |_   _
     | |_) | | | |_  / _` |/ _` | '__/ _` | | | | | | | |
     |  _ <| |_| |/ / (_| | (_| | | | (_| | |_| | | |_| |
     |_| \_\\__,_/___\__, |\__,_|_|  \__, |\__,_|_|\__,_|
                     |___/           |___/               """
    print "\n"


if __name__ == '__main__':
    bs = BookStore()
    print_ascii()
    print "Ozgur Barkod Okuyucu v1.0"
    bs.main()