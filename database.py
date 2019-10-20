from re import findall,sub
from lxml import html
from time import sleep
from selenium import webdriver
from pprint import pprint
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user='root',
    password='mySQL',
    database='mydatabase'
)

def parse(url):
    searchKey = "Boston"  # Change this to your city
    checkInDate = '10/19'  # Format %d/%m/%Y
    checkOutDate = '10/20'  # Format %d/%m/%Y
    response = webdriver.Chrome()
    response.get(url)
    searchKeyElement = response.find_elements_by_xpath('//input[contains(@id,"destination")]')
    checkInElement = response.find_elements_by_xpath('//input[contains(@class,"check-in")]')
    checkOutElement = response.find_elements_by_xpath('//input[contains(@class,"check-out")]')
    submitButton = response.find_elements_by_xpath('//button[@type="submit"]')
    if searchKeyElement and checkInElement and checkOutElement:
        searchKeyElement[0].send_keys(searchKey)
        checkInElement[0].clear()
        checkInElement[0].send_keys(checkInDate)
        checkOutElement[0].clear()
        checkOutElement[0].send_keys(checkOutDate)
        randomClick = response.find_elements_by_xpath('//h1')
        if randomClick:
            randomClick[0].click()
        submitButton[0].click()
        sleep(15)
        dropDownButton = response.find_elements_by_xpath('//fieldset[contains(@id,"dropdown")]')
        if dropDownButton:
            dropDownButton[0].click()
            priceLowtoHigh = response.find_elements_by_xpath('//li[contains(text(),"low to high")]')
            if priceLowtoHigh:
                priceLowtoHigh[0].click()
                sleep(10)

    mycursor = mydb.cursor()
    mycursor.execute("""truncate table hotels""")#clean table
    mydb.commit()
    parser = html.fromstring(response.page_source, response.current_url)
    hotels = parser.xpath('.//section[@class="hotel-wrap"]')
    for hotel in hotels[:10]:  # Replace 5 with 1 to just get the cheapest hotel
        hotelName = hotel.xpath('.//h3[@class="p-name"]/a')
        hotelName = hotelName[0].text_content() if hotelName else None
        price = hotel.xpath('.//div[@class="price"]/a//ins')
        price = price[0].text_content().replace(",", "").strip() if price else None
        if price == None:
            price = hotel.xpath('.//div[@class="price"]/a')
            price = price[0].text_content().replace(",", "").strip() if price else None
        price = findall('([\d\.]+)', price) if price else None
        price = price[0] if price else None
        rating = hotel.xpath('.//div[@class="reviews-box resp-module"]')
        rating = rating[0].text_content()
        rating = findall('([\d.]+)', rating)[0]
        sql = "INSERT INTO hotels (hotelname,price,rating) VALUES (%s,%s,%s)"
        val = (hotelName,price,rating)
        mycursor.execute(sql,val)
        mydb.commit()
        """item = {
            "hotelName": hotelName,
            "price": price,
            "rating": rating,
        }
        pprint(item)"""
    mycursor.execute("SELECT * FROM hotels ORDER BY rating DESC , price")
    for x in mycursor.fetchall():
        print(x)



if __name__ == '__main__':
    parse('http://www.hotels.com')

