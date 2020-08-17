# Import Libraries
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import grequests

# This function pulls the URLs which will be scraped from
def get_URLs(input_data):
    # Initialize empty return variables
    urls = list()
    urls2 = list()
    # Make new DF of symbol column to pull URLs from
    pf = pd.DataFrame(input_data, columns= ['Symbol'])
    for i in range(0,len(pf['Symbol'])):
        # Format symbol column for webscraping
        pf.at[i, 'Symbol'] = pf.at[i, 'Symbol'].replace("-",".")
        # Get URL list
        url = ('https://ycharts.com/companies/%s' % pf.at[i, 'Symbol'])
        urls.append(url)
    for j in range(0,len(pf['Symbol'])):
        # Get URL list for second set of scraping
        url2 = ('https://ycharts.com/companies/%s/holdings' % pf.at[j, 'Symbol'])
        urls2.append(url2)
    return urls, urls2

# This function returns a list of Name values from the Tickers (Not standard input from yf, needs to be scraped)
def namescrape(urls):
    # Initialize empty return variable
    names = list()
    # Async requests
    reqs = [grequests.get(url) for url in urls]
    resp = grequests.map(reqs)
    # Parse data with BS4 and append data to return variable
    for r in resp:
        get_text = r.text
        soup = BeautifulSoup(get_text, "lxml")
        try:
            for div in soup.findAll('h1', attrs={'class':'securityName'}):
                name= div.find('a').contents[0]
                names.append(name)
        except:
            pass
        else:
            for div in soup.findAll('h1', attrs={'class':'index-name-text'}):
                name= div.string
                name = name.replace("\n", "")
                name = name[24:]
                names.append(name)
    return names

# This function returns a cleaned up version of the user input to be printed back to the user and initalize variables for the main function
def print_input(input_data, names):
    # Get DF from CSV
    pf = pd.DataFrame(input_data, columns= ['Symbol', 'Name', 'Current Price', 'Quantity'])
    # Add scraped Names
    pf['Name'] = names
    # Create dict of ETF names to append to final print out
    etfnames = {}
    for i in range(0,len(pf['Name'])):
        if 'ETF' in pf.at[i, 'Name']:
            etfnames.setdefault(pf.at[i,'Symbol'], pf.at[i,'Name'] )
    # Seperate Cdn and US equities by defining str
    cdn1 = '.TO'
    cdn2 = '.V'
    # Define live currency exchange using exchange API
    r = requests.get('https://api.exchangeratesapi.io/latest?base=USD&symbols=CAD')
    j = r.json()
    x = float(j['rates']['CAD'])
    # US/CAD Current Price calculation
    for i in range(0,len(pf['Current Price'])):
        pf.at[i, 'Symbol'] = pf.at[i, 'Symbol'].replace("-",".")
        # if .TO is not in symbol OR .V is not in symbol, then
        if not cdn1 in pf.at[i,'Symbol'] or cdn2 in pf.at[i,'Symbol']:
            # Update price based on exchange rate
            pf.at[i,'Current Price'] *= x
    # Calculate total value
    totval = pf['Current Price'] * pf['Quantity']
    pf['Total Value'] = totval
    # Weight of Portfolio calculation
    pft= pf['Total Value'].sum()
    wt = pf['Total Value'] / pft 
    pf ['% Weight'] = wt
    # Clean up pf to only include required columns
    del pf['Total Value']
    del pf['Current Price']
    del pf['Quantity']
    # Clean up user input for print out
    pf1 = pf.sort_values(by = '% Weight', ascending=False)
    valu = pft * pf1['% Weight']
    pf1['Total Value'] = valu
    per = 100 * pf1['% Weight']
    pf1['% Weight'] = per
    pf1['Total Value'] = pf1['Total Value'].round(decimals=2)
    pf1['% Weight'] = pf1['% Weight'].round(decimals=3)
    # Return results
    return pf1.to_html(index=False), pft.round(decimals=2), etfnames, pf, pft

# This function converts the input data into the list of holdings and weightings from the ETF Tickers
def convert(urls2, pf, pft, etfnames):
    # Start empty list of ETF holdings
    etf_lib = list()
    # Async requests
    reqs = [grequests.get(url) for url in urls2]
    resp = grequests.map(reqs)
    # Parse data tables with pandas and append data to return variable
    for i, r in enumerate(resp):
        get_text = r.text
        try:
            wds=pd.read_html(get_text)[1]
        # This statement skips equities so the scraper can pull ETF data only
        except:
            pass
        else:
            wds = wds.rename(columns={"%\xa0Weight": "% Weight", "%\xa0Change" : "% Chg"})
            # Filter col of interest and convert '% Weight' col from str to float, format Symbol col
            for j in range(0,len(wds['% Weight'])):
                wds.at[j, '% Weight'] = wds.at[j, '% Weight'].replace("%","")
                wds.at[j, 'Symbol'] = wds.at[j, 'Symbol'].replace("-",".")
            wds['% Weight'] = wds['% Weight'].astype(float)
            # Delete unused data
            del wds['Price']
            del wds['% Chg']
            # Create MISC ticker which represents the % holding of the ETF not accouted for by top 25 holdings
            etft= 100 - wds['% Weight'].sum()
            new_row= {'Symbol':(pf.at[i, 'Symbol']), '% Weight':etft}
            wds = wds.append(new_row, ignore_index=True)
            # Multiply ETF ticker list by weight in portfolio
            wds['% Weight'] = wds['% Weight'] * pf.at[i, '% Weight']
            # Append to list of ETF data and remove ETF ticker from list and remove original ticker entry after it has been parsed
            etf_lib.append(wds)
            pf.drop([i], inplace=True)
    # Concatenate lists together and sum any repeat tickers in list
    df = pd.concat(etf_lib)
    pf['% Weight'] *= 100
    df = df.append(pf)
    # Save names as a dict object with symbols as keys and names as values
    names = dict(zip(df['Symbol'], df['Name']))
    # This command will combine repeat tickers and sum their values, but doing so deletes the Name col
    df = df.groupby(['Symbol'] , as_index=False).sum()
    out = df.sort_values(by = '% Weight', ascending=False)
    # Add empty Name col to out df and re-index
    out["Name"] = ['' for _ in range(len(out))]
    columnsTitles = ['Symbol', 'Name', '% Weight', 'Total Value']
    out = out.reindex(columns=columnsTitles)
    # Correct name column to values saved in names dictionary
    for i in range(0,len(out['Symbol'])):
        for j in names.keys():
            if str(j) == str(out.at[i, 'Symbol']):
                out.at[i, 'Name'] = names.get(j)
    # Re-add ETF Names
    for i in range(0,len(out['Symbol'])):
        for j in etfnames.keys():
            if str(j) in str(out.at[i, 'Symbol']):
                out.at[i, 'Name'] = ('Misc ' + str(etfnames.get(j)) + ' Holdings')
    # Update and format before print out
    val = pft * (out['% Weight'] / 100)
    out ['Total Value'] = val             
    out['Total Value'] = out['Total Value'].round(decimals=2)
    out['% Weight'] = out['% Weight'].round(decimals=3)
    # Return result
    return out