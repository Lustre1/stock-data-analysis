'''
This module accesses nasdaq APIs to scrape stock data for analyzation

Resources used:
https://docs.python.org/3/library/urllib.request.html
https://medium.com/@danielhalwell/a-comprehensive-guide-to-web-scraping-with-python-using-the-requests-library-3eaf2bb8dfd7
https://docs.python.org/3/library/gzip.html
https://docs.python.org/3/library/datetime.html
https://docs.python.org/3/library/statistics.html
https://www.geeksforgeeks.org/how-to-use-sys-argv-in-python/
https://docs.python.org/3/library/functions.html#open
'''
from urllib.request import Request, urlopen
from json import loads, dump
from gzip import decompress
from datetime import date
from statistics import mean, median
from sys import argv

def download_data(ticker: str) -> dict:
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
        print("The server could not be reached")
        return {}

    # Decompresses the gzip compressed data
    try:
        data = decompress(data)
    except:
        print("The data was not compressed with gzip or could not be decompressed")
        return {}
    
    # Converts the json data to a python dictionary and gets the data list
    try:
        data = loads(data)
        if data["status"]["rCode"] != 200:
            print("The ticker does not exist")
            return {}
        data = data["data"]
    except:
        print("The data format is not in json or there is no data")
        return {}

    return data


def process_data(data: dict) -> dict:
    '''Parses the stock data dictionary to find the min, max, mean, and median value'''
    
    # Exits if there is no data
    if data == {}:
        return {}

    # Removes unnecessary data and sorts the closing prices
    closing_prices = []
    try:
        for day in data["chart"]:
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
        "median": median(closing_prices),
        "ticker": data["symbol"]
    }
    
    return stats

def store_json(json_data: list) -> None:
    '''Asks the user about storing json data in a file'''
    file = None
    file_name = ""

    while not file and file_name.lower() != "cancel":
        file_name = input("Enter a name for a storage file or \"cancel\" to quit: ")
        
        if file_name.lower() != "cancel":
            try:
                # Checks if the file name is already used to avoid overriting files
                file = open(file_name, "r")
                file.close()

                # Prompts the user about overriting the file
                response = input("A file with that name already exists.\nAre you sure you want to overwrite it (yes or no)? ").lower()
                while response[0] != "y" and response[0] != "n":
                    response = input("Your response was invalid.\nAre you sure you want to overwrite the file (yes or no)? ").lower()
                
                # If yes, overrites the file, otherwise, allows selecting a new name
                if response[0] == "y":
                    try:
                        file = open(file_name, "w")
                    except:
                        print("The file could not be written to")
                        file = None
                else:
                    file = None
            
            except:
                # Creates a new file if the file name is not already used
                try:
                    file = open(file_name, "w")
                except:
                    print("The file could not be written to")
                    file = None

    # Writes the json data to the file
    if file:
        try:
            dump(json_data, file)
        except:
            print("The json data could not be written to the file")
        file.close()


stats_list = []

# Handles ticker symbols as command line arguments
if len(argv) > 1:
    for ticker in argv[1:]:
        stats = process_data(download_data(ticker))
        if stats:
            stats_list.append(stats)
else:
    # Handles ticker symbols during runtime
    ticker = ""
    while ticker != "STOP":
        ticker = input("Enter a ticker symbol or \"stop\" to proceed: ").upper()
        if ticker != "STOP":
            stats = process_data(download_data(ticker))
            if stats:
                stats_list.append(stats)

# Prints the data to the console
print("\nData:")
for stats in stats_list:
    print(stats)
print()

store_json(stats_list)
