# Tool for Gathering Historical and Live URLs
- __This Python script is designed to gather historical URLs from the Wayback Machine API and Common Crawl API, and live URLs using various web crawling tools. It takes a list of subdomains as input and outputs discovered URLs related to those subdomains.__
## Features
- Retrieves historical URLs from Wayback Machine API.
- Retrieves historical URLs from Common Crawl API.
- Uses web crawling tools (hakrawler, katana, getJS, gau) to find live URLs.
- Outputs discovered URLs related to provided subdomains.
## Dependencies
- Ensure you have Python 3.x installed on your system. The script relies on the following Python libraries:
  - requests: For making HTTP requests to APIs.
  - subprocess: For executing external commands (required by crawling tools).
  - Additional tools ([hakrawler](https://github.com/hakluke/hakrawler), [katana](https://github.com/projectdiscovery/katana), [getJS](https://github.com/003random/getJS), [gau](https://github.com/lc/gau)) should be installed and accessible via the command line.
## Installation
1. Clone the repository:
```
git clone https://github.com/emre-bi/urls.git
cd repository
```
2. Install Python dependencies:
```
pip install -r requirements.txt
```
3. Install additional tools ([hakrawler](https://github.com/hakluke/hakrawler), [katana](https://github.com/projectdiscovery/katana), [getJS](https://github.com/003random/getJS), [gau](https://github.com/lc/gau)).

## Usage
1. Prepare a file containing subdomains (one per line), e.g., subdomains.txt.
2. Run the script by piping the subdomains file into it:
```
cat subdomains.txt | python3 app.py
```
3. The script will fetch historical URLs from Wayback Machine and Common Crawl APIs, and use the specified crawling tools to find live URLs associated with each subdomain.
4. Results will be printed to stdout
