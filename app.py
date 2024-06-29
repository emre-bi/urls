import argparse
import sys
from modules.get_urls_api import get_result_urls, remove_unnecessary_urls
from modules.other_tools import get_other_urls, run_linkfinder


##### User Input #####
parser = argparse.ArgumentParser(description="Collect urls for a spesfied domain")
parser.add_argument('domain', nargs='*', type=str, help="Domain name(s) to get urls for")
parser.usage = """app.py [-h] [domain ...]
Examples:
  cat domains.txt | python3 app.py
"""
args = parser.parse_args()
domain_names = args.domain

if not domain_names:
        # Check if stdin has any input
        if sys.stdin.isatty():
            print("Warning: No domain names provided as input. Exiting.")
            sys.exit(1)
        else:
            domain_names = [line.strip() for line in sys.stdin.readlines()]

##### Urls From Sources #####
for domain in domain_names:
    #hist_urls = get_result_urls(domain)

##### Urls From Other-Tools #####
    if not (domain.startswith("http://") or domain.startswith("https://")):
        domain = "http://" + domain
    other_urls = get_other_urls(domain)

    all_urls =  other_urls # + hist_urls
    urls_from_js = []
    urls1 = []
    urls2 = []
    if all_urls is not None:
        urls1, js_urls = remove_unnecessary_urls(all_urls)
        for js_url in js_urls:
            urls_from_js.append(run_linkfinder(js_url))
    
    
    for url_list in urls_from_js:
        urls2 = url_list + urls2
    
    urls = urls1 + urls2

    last_urls, _ = remove_unnecessary_urls(urls)
    
    for url in last_urls:
        print(url)