'''
This module accesses nasdaq APIs to scrape stock data for analyzation

Resources used:
https://docs.python.org/3/library/urllib.request.html
https://medium.com/@danielhalwell/a-comprehensive-guide-to-web-scraping-with-python-using-the-requests-library-3eaf2bb8dfd7
https://docs.python.org/3/library/gzip.html
https://docs.python.org/3/library/datetime.html
https://docs.python.org/3/library/statistics.html
'''
from urllib.request import Request, urlopen
from json import loads, dump
from gzip import decompress
from datetime import date
from statistics import mean, median

def download_data(ticker: str) -> list:
    '''
    This function scrapes nasdaq stock data using a header to appear as a web browser,
    then decompresses the gzip data and converts the json data to a python dictionary
    '''
    # Constructs the URL using the ticker symbol entered and the current date to get the past 5 years of data
    # I found this URL by inspecting the page and looking through the Network tab for json files
    today = date.today()
    todate = today.isoformat()
    today = today.replace(year = today.year-5)
    url = f"https://api.nasdaq.com/api/quote/{ticker.upper()}/chart?assetclass=stocks&fromdate={today.isoformat()}&todate={todate}"

    # Header to appear as a web browser
    headers = {
        "Host": "api.nasdaq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.nasdaq.com/",
        "Origin": "https://www.nasdaq.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers"
    }

    # Requests the data from nasdaq
    req = Request(url, headers = headers)
    try:
        data = urlopen(req, timeout = 5).read()
    except:
        print("The server could not be reached or the ticker doesn't exist")
        return []

    # Decompresses the gzip compressed data
    try:
        data = decompress(data)
    except:
        print("The data was not compressed with gzip or could not be decompressed")
        return []
    
    # Converts the json data to a python dictionary and gets the data list
    try:
        data = loads(data)["data"]["chart"]
    except:
        print("The data format is not in json or there is no data")
        return []

    return data

def process_data(data: list) -> dict:
    '''Parses the stock data dictionary to find the min, max, mean, and median value'''
    
    # Exits if there is no data
    if data == []:
        print("There is no data to process")
        return {}

    # Removes unnecessary data and sorts the closing prices
    closing_prices = []
    try:
        for day in data:
            closing_prices.append(day["y"])
        closing_prices.sort()
    except:
        print("The data could not be parsed")
        return {}
    
    # Produces statistic results dictionary
    stats = {
        "min": closing_prices[0],
        "max": closing_prices[-1],
        "avg": mean(closing_prices),
        "median": median(closing_prices)
    }
    
    return stats

print(process_data(download_data("msft")))