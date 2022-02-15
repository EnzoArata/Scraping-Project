from bs4 import BeautifulSoup
import requests
from lxml import etree
import csv
#set all pages of colleges into URL list
urls = ["https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=1", "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=2", "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=3",
        "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=4", "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=5", "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=6",
        "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=7"]
#appendUrl will be used later when ids for every page is found
appendUrl = "https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&sp=4&pg=1&id="
collegeUrlList = []

#use page urls to gather and collect all college specific URLS
for url in urls:
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    myTr = soup.find_all("tr")
    #
    #Get line from Table row
    #parse it into link form
    #
    for tr in myTr:
        if tr.td.td != None:

            tempString = str(tr.a)
            #Added special case for University of the Virgin Islands-Albert A. Sheen
            #Get ID of webpage from URL
            if tempString[48] == '>':
                subString = tempString[41:47]
            else:
                subString = tempString[41:49]
            collegeUrlList.append(appendUrl+subString)
            
#Set Headers for CSV file and write in first row
header = ['Name', 'Street', 'City', 'State', 'Zip', 'Phone', 'Website', 'Type', 'Awards', 'Campus Setting', 'Campus Housing', 'Student Population', 'Student to Faculty Ratio']
with open("data.csv", 'w') as csvfile:
    csvwriter = csv.writer(csvfile)

    csvwriter.writerow(header)

#Go through all gathered college specific Urls
for url in collegeUrlList:
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "html.parser")
    myEtree = etree.HTML(str(soup))
    collegeName = soup.find("span", class_="headerlg").text
    collegeName = str(collegeName)
    #Use Xpath to get data that contains complete address
    address = str(myEtree.xpath('//*[@id="RightContent"]/div[4]/div/div[2]/span/text()'))
    street = " "
    city = " "
    state = " "
    zip = " "
    #parse address into smaller segments for data points
    for i in range(2, len(address)):
        if address[i] ==',':
            if street == " ":
                street = address[2:i]
                continue
            if city == " ":
                city = address[4+len(street):i]
                if address[len(address)-7] == "-":
                    state = address[6+len(street)+len(city):len(address)-12]
                    zip = address[len(address)-12:len(address)-2]
                else:
                    state = address[6+len(street)+len(city):len(address)-7]
                    zip = address[len(address)-7:len(address)-2]
                continue

    #Get Table containg college data
    myTable = soup.find("table", class_="layouttab")
    #Get first row with phone info
    myRow = (myTable.findAll("tr")[0]).text
    phone = str(myRow)
    phone = phone[len(phone)-14:len(phone)]

    #Get 2nd row with webstie info
    myRow = (myTable.findAll("tr")[1]).text
    website = str(myRow)
    website = website[10:len(website)]

    #get 3rd row with type of college
    myRow = (myTable.findAll("tr")[2]).text
    type = str(myRow)
    type = type[7:len(type)]

    #get 4th row with award data
    myRow = (myTable.findAll("tr")[3]).text
    awards = str(myRow)
    awards = awards[17:len(awards)]

    #get 5th row with campus setting
    myRow = (myTable.findAll("tr")[4]).text
    setting = str(myRow)
    setting = setting[17:len(setting)]

    #get 6th row for campus Housing
    myRow = (myTable.findAll("tr")[5]).text
    housing = str(myRow)
    housing = housing[17:len(housing)]

    #get 7th row for student population
    myRow = (myTable.findAll("tr")[6]).text
    population = str(myRow)
    population = population[21:len(population)]

    #get 8th row for student to faculty ratio, if it exists
    #there is one college without a faculty ratio
    if len(myTable)>7:
        myRow = (myTable.findAll("tr")[7]).text
        ratio = str(myRow)
        ratio = ratio[27:len(ratio)]
    else:
        ratio = "NA"
        
    #write new row to table
    with open("data.csv", 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        data = [collegeName, street, city, state, zip, phone, website, type, awards, setting, housing, population, ratio]
        csvwriter.writerow(data)

        csvfile.close()
