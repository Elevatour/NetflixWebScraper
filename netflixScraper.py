import re, requests, json, sys, os, pickle
from bs4 import BeautifulSoup as bs
from time import sleep

def scrapeData(url, category, dictionary):

    results = []
    unitColor = "\033[5;36m\033[5;47m"
    endColor = "\033[0;0m\033[0;0m"
    page = requests.get(url)
    soup = bs(page.content, "html.parser")
    data = soup.findAll("section", "nm-collections-row")
    result = "["
    length = 0
    i = 0

    for lists in data:
        entries = lists.findAll("li", "nm-content-horizontal-row-item")
        length += len(entries)

    sys.stdout.write("\"%s\"" % category + " with a capacity of %d \n" % length)

    for temp in data:

        genre = temp.find("span", "nm-collections-row-name")
        genre = genre.text if genre else temp.find("h1", "nm-collections-row-name").text
        items = temp.findAll("li", "nm-content-horizontal-row-item")
    
        for item in items:

            increase = int(50.0 / length * i)
            title = item.find("span", "nm-collections-title-name")
            checkItem = False
            
            if len(dictionary) != 0:

                count = 0
                check = False
                l = len(dictionary)

                while count < len(dictionary):
                    if title.text == dictionary[count]["title"]:
                        check = True
                        break
                    count += 1

                if not check:
                    dictionary.append({ "title": title.text })
                    image = item.find("a", "nm-collections-title nm-collections-link")
                    result += setJsonData(str(title.text), str(image["href"])) + ("," if item != items[-1] else "")
                    checkItem = True

            else:
                dictionary.append({ "title": title.text })
                image = item.find("a", "nm-collections-title nm-collections-link")
                result += setJsonData(str(title.text), str(image["href"])) + ("," if item != items[-1] else "")
                checkItem = True
            
            sys.stdout.write("\r|%s%s%s%s| %d%%" % (unitColor, "\033[7m" + " "*increase + " \033[27m", endColor, " "*(50-increase), 2*increase))
            i += 1
        
        result += "," if not result.endswith(",") and checkItem else ""

    sys.stdout.write("\r" + "|%s%s%s| %d%%" % (unitColor, "\033[7m" + " "*20 + "COMPLETE!" + " "*21 + " \033[27m", endColor, 100) + "\n")
    if result.endswith(","):
        result = result[:-1]

    result += "]"
    sys.stdout.flush()
    results.append(result)
    results.append(dictionary)
    return results

def scrapeImage(soup):

    data = soup.find("div", "hero-image hero-image-desktop")
    styles = data["style"].split(";")

    for style in styles:
        if style.find("background-image") == 0:
            return style.replace("background-image:url(\"", "").replace("\")", "")

def setJsonData(title, url):

    page = requests.get(url)
    soup = bs(page.content, "html.parser")
    summary = str(soup.find("div", "title-info-synopsis").text)
    year = str(soup.find("span", "title-info-metadata-item item-year").text) if soup.find("span", "title-info-metadata-item item-year") else "none"
    maturity = int(soup.find("span", "maturity-rating").text)
    actors = str(soup.find("span", "title-data-info-item-list").text) if soup.find("span", "title-data-info-item-list") else "none"
    return (
        json.dumps({
            "title": title,
            "imgSrc": scrapeImage(soup),
            "duration": str(soup.find("span", "duration").text),
            "genre": str(soup.find("a", "title-info-metadata-item item-genre").text),
            "summary": summary,
            "published": year,
            "starring": actors,
            "maturity": maturity
        }, ensure_ascii=False).encode("utf8").decode() if soup.find("span", "duration") else (
        json.dumps({
            "title": title,
            "imgSrc": scrapeImage(soup),
            "duration": str(soup.find("span", "duration").text),
            "genre": str(soup.find("a", "title-info-metadata-item item-genre").text),
            "summary": summary,
            "published": year,
            "starring": actors,
            "maturity": maturity
        }, ensure_ascii=False).encode("utf8").decode()))

def queryData(category, fileName, url):

    dictionaryPath = "netflix.dictionary"

    if os.path.exists(dictionaryPath):  
        dictionary = [] if os.path.getsize(dictionaryPath) == 0 else pickle.load(open(dictionaryPath, "r+b"))
    else:
        dictionary = []

    returnData = scrapeData(url, category, dictionary)

    if os.path.exists(fileName) and os.path.getsize(fileName) > 0:
        readFile = open(fileName, "r+", encoding="utf-8")
        if len(returnData[0]) > 2:
            momentaryData = json.load(readFile)
            momentaryData.append(json.load(returnData[0][1:][:-1]))
            readFile.close()
            with open(fileName, "w") as file:
                json.dump(momentaryData, file)
        else:
            readFile.close()

    else:
        with open(fileName, "w", encoding="utf-8") as file:
            file.write(returnData[0])

    with open(dictionaryPath, "wb") as file:
        pickle.dump(returnData[1], file)

queryData("documentations", "documentation.json", "https://www.netflix.com/de/browse/genre/6839")
queryData("series", "series.json", "https://www.netflix.com/de/browse/genre/83")
queryData("movies", "movies.json", "https://www.netflix.com/de/browse/genre/34399")