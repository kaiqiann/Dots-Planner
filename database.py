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

def hotel(url):
    print("Enter Destination:")
    searchKey = input()  # Change this to your city
    print("Enter Check In Date: (Format month/day/year)")
    checkInDate =  input() # Format %d/%m/%Y
    print("Enter Check out Date: (Format month/day/year)")
    checkOutDate = input()  # Format %d/%m/%Y
    print("Enter your Preference:\n"
          "1. low price,\n"
          "2. close to city center\n"
          "3. parking lot available\n"
          "4. High rating \n")
    preference = input()
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
        sleep(1)
        submitButton[0].click()
        sleep(1)
        dropDownButton = response.find_elements_by_xpath('//fieldset[contains(@id,"dropdown")]')
        if dropDownButton:
            dropDownButton[0].click()
            priceLowtoHigh = response.find_elements_by_xpath('//li[contains(text(),"low to high")]')
            if priceLowtoHigh:
                priceLowtoHigh[0].click()
                sleep(1)

    mycursor = mydb.cursor()
    mycursor.execute("""truncate table hotels""")#clean table
    mydb.commit()
    parser = html.fromstring(response.page_source, response.current_url)
    hotels = parser.xpath('.//section[@class="hotel-wrap"]')
    temp1 = 'http://www.hotels.com'
    for hotel in hotels[:10]:  # Replace 10 with 1 to just get the cheapest hotel
        hotelName = hotel.xpath('.//h3[@class="p-name"]/a')
        hotelName = hotelName[0].text_content() if hotelName else None
        #hotel prices
        price = hotel.xpath('.//div[@class="price"]/a//ins')
        price = price[0].text_content().replace(",", "").strip() if price else None
        if price == None:
            price = hotel.xpath('.//div[@class="price"]/a')
            price = price[0].text_content().replace(",", "").strip() if price else None
        price = findall('([\d\.]+)', price) if price else None
        price = price[0] if price else None
        #hotel rates
        rating = hotel.xpath('.//div[@class="reviews-box resp-module"]')
        rating = rating[0].text_content() if rating else None
        rating = findall('([\d.]+)', rating)[0]

        #distance to city center
        location = hotel.xpath('.//ul[@class="property-landmarks"]/li')
        location = location[0].text_content() if location else None
        location = findall('([\d.]+)', location)[0]
        #print(location)

        #url link
        temp = hotel.xpath('.//a[@class="cta"]')
        if temp:
            propertynl = temp[0].attrib['href'] if temp else None
            propertynl = temp1 + propertynl
        #parking
        parking = hotel.xpath('.//li[@class="hmvt8258-amenity parkingOptions"]/li')
        #parking = parking[0].text_content() if parking else None
        if parking is not None:
            parking = 1
        else:
            parking = 0
        #print(parking)

        sql = "INSERT INTO hotels (hotelname, price, rating, location, parking, link) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (hotelName, price, rating, location, parking, propertynl)
        mycursor.execute(sql, val)
        mydb.commit()
        """item = {
            "hotelName": hotelName,
            "price": price,
            "rating": rating,
        }
        pprint(item)"""
    mycursor.execute("SELECT * FROM hotels ORDER BY price")# default price is the preference
    if preference is 1:
        mycursor.execute("SELECT * FROM hotels ORDER BY price")
    elif preference is 2:
        mycursor.execute("SELECT * FROM hotels ORDER BY location")
    elif preference is 3:
        mycursor.execute("SELECT * FROM hotels ORDER BY parking DESC ")
    elif preference is 4:
        mycursor.execute("SELECT * FROM hotels ORDER BY rating DESC ")

    p = 0
    for x in mycursor.fetchall():
        if p == 0:
            print(x[6])
        p = 1


if __name__ == '__main__':
    print("//////Dotsplanner//////")
    print("Hotel? Y/N")
    if input() == "Y":
        hotel('http://www.hotels.com')
    """print("Plane Tickets? Y/N")
    if input() == "Y":
        planetickets('https://travel.hotels.com/?intlid=HOME+%3A%3A+header_main_section')"""

