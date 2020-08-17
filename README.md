# ETF Converter
**For a live demo, please visit https://etfconverter.herokuapp.com/. There is also a GIF loop of the demo file included in this README.**

***This app is meant for personal/project use only and the live demo is not secure.***

ETF Converter is a simple site which takes csv input from a user's Yahoo Finance data, and returns underlying ETF holdings and the resulting overall exposure to individual companies.

It's written using Flask in python3, and primarily uses pandas and asynchronous webscraping (grequests, Beautiful soup) to convert user input. Front end is HTML with some Jinja and the CSS is mainly from Pure-CSS.

## Demo
![](https://raw.githubusercontent.com/willzittlau/ETFsite/master/demo.gif)

## Installation

Download all of the files and folders from Github and add it to a new project path. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries outlined in requirements.txt. Make sure that the folder structure is kept consistent between the package downloaded from Github and your project path. If planning to run locally, uncomment out the python # tags on app.py indicating local use and comment out the Heroku ones.

```bash
$ pip install -r requirements.txt
```

## Usage

To launch this site locally, run app.py and navigate to your local host address. In another tab, log into your Yahoo Finance account and open the portfolio containing ETFs that you are looking to analyze. Download this portfolio as a .csv file and save it somewhere on your CPU. Go back to local host, and use the drag 'n drop upload box to upload the csv data to the server. Wait a moment (Larger portfolios will take longer to analyze) and the sript will execute. A new page will load returning a table view with a breakdown of the data which was received, and a download link to the results. Click on the 'Download' button to download the results as a .csv to your CPU.

```bash
$ py app.py
```
    http://127.0.0.1:5000/

Alternatively, you can also use the demo site provided, however, file uploads are not secure!

*_There is already a quotes.csv file added to the project folder to use as a demo file. For actual use, delete this demo file and replace it with the quotes.csv downloaded from your Yahoo Finance portfolio. This .csv file can be anywhere on your computer, it doesn't need to stay in the project folder._

## Limitations

This script only works for portfolios containing US and Canadian equitities traded on the major exchanges. This means that it will only work with ETFs and individual stocks, not things like precious metals, cash equivalents, or mutual funds etc. Also, only the top 25 holdings from each ETF can be pulled, so any remaining value will be added back to the original ETF ticker name with a 'Misc' notation added. If ycharts changes their site structure, the script will break.

## Contributing

Feel free to take this template and edit it however you would like. I would love to hear about any improvements you make!

## License
[MIT](https://choosealicense.com/licenses/mit/) Free Usage
