import requests
import json
import time
import re
import sys
import logging
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# f"http://index.commoncrawl.org/CC-MAIN-2018-22-index?url={subdomain}/*&output=json&showNumPages=true"
# https://www.virustotal.com/vtapi/v2/domain/report?apikey=%s&domain=%s
# f"http://web.archive.org/cdx/search/cdx?url={subdomain}/*&collapse=urlkey&output=json"


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)


######### Get Urls From Wayback #########
def get_url_from_wayback(domain):
    logger.info(f"Executing get_url_from_wayback for domain: {domain}")

    cdx_api_url = "http://web.archive.org/cdx/search/cdx"

    params = {
        'url': f"{domain}/*",
        'output': 'json',
        'fl': 'original',
        'collapse': 'urlkey',
        'filter': 'statuscode:200'
    }
    
    try:
        response = requests.get(cdx_api_url, params=params, timeout=10)
    except Exception as e:
        logger.error(f"Exception occurred during request in get request to the archieve: {e}")

    if response.status_code == 200:
        data = response.json()
        
        # The first item in the response is the header, so we skip it
        urls = [item[0] for item in data[1:]]
        unique_urls = list(set(urls))
        return unique_urls
    else:
        logger.error("Failed to retrieve data From archieve api")
        return []
    

######### Get Urls From CommonCrawl #########


def list_available_indexes():
    logger.info("Executing list_available_indexes")

    cc_indexes_url = "https://index.commoncrawl.org/collinfo.json"
    try:
        response = requests.get(cc_indexes_url, verify=False, timeout=10)
    except Exception as e:
        logger.error(f"Exception occurred during request: {e}")
        return []
    
    if response.status_code == 200:
        indexes = response.json()
        return [index['id'] for index in indexes]
    else:
        logger.error("Failed to retrieve index list")
        return []


def get_urls_from_commoncrawl(domain):
    logger.info(f"Executing get_urls_from_commoncrawl for domain: {domain}")

    urls = []
    indexes = list_available_indexes()

    for index in indexes:
        logger.info(f"Processing index: {index}")
        
        cc_index_url = f"http://index.commoncrawl.org/{index}-index"
        params = {
            'url': f"{domain}/*",
            'output': 'json',
            'fl': 'url'
        }

        page = 0
        page_size = 10000
        max_retries = 4
        retry_delay = 1

        while True:
            params['page'] = page
            params['pageSize'] = page_size
            
            try:
                response = requests.get(cc_index_url, params=params, timeout=10)
                response.raise_for_status()
                content = response.content.decode("UTF-8")
                # Process the response content to extract URLs
                lines = content.splitlines()
                if not lines:
                    break

                for line in lines:
                    try:
                        url_data = json.loads(line)
                        urls.append(url_data['url'])
                    except json.JSONDecodeError as e:
                        continue

                # If fewer results than page_size are returned, it's likely the last page
                if len(lines) < page_size:
                    break

                # Increment page for the next request
                page += 1  
                # DELAY for rate limiting
                time.sleep(retry_delay)

            except requests.exceptions.Timeout:
                time.sleep(retry_delay)
                continue
            except requests.exceptions.RequestException as e:
                logger.error(f"GET Request Error in CommonCrawl for index-> {index} ------>>>>: {e}")
                if 'SlowDown' in str(e):
                    if max_retries > 0:
                        time.sleep(retry_delay)
                        max_retries -= 1
                        continue
                    else:
                        logger.error(f"Max retries reached for index {index}.")
                        break
                else:
                    logger.error(f"RequestException occurred: {e}")
                    break
            

    unique_urls = list(set(urls))
    return unique_urls
    

######### Remove Unnecessary Things #########

def normalize_to_http(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == "https":
        parsed_url = parsed_url._replace(scheme="http")
    return urlunparse(parsed_url)


def remove_unnecessary_urls(urls):
    logger.info(f"Executing URL Filtering")

    # Unnecessary Extentions
    unnecessary_extensions = [
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico', '.tiff', '.tif',
    '.woff', '.woff2', '.ttf', '.otf', '.eot', '.fon',
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.csv', '.rtf',
    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg', '.webm'
    ]
    pattern = re.compile(r'\.(' + '|'.join([ext[1:] for ext in unnecessary_extensions]) + r')(\?.*)?$', re.IGNORECASE)    
    filtered_urls = [url for url in urls if not pattern.search(url)]
    js_pattern = re.compile(r'\.(' + '|'.join(['js']) + r')(\?.*)?$', re.IGNORECASE)
    js_urls = [url for url in urls if js_pattern.search(url)]
       
    # Dups because multiple parameters, either diffrent paramater or same parameter but diffrent value
    
    path_to_params = {}

    for url in filtered_urls:
        normalized_url = normalize_to_http(url)
        parsed_url = urlparse(normalized_url)
        path = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
        params = parse_qs(parsed_url.query)

        if path not in path_to_params:
            path_to_params[path] = params
        else:
            for key, value in params.items():
                if key in path_to_params[path]:
                    pass
                else:
                    path_to_params[path][key] = value

    merged_urls = []
    for path, params in path_to_params.items():
        query_string = urlencode(params, doseq=True)
        merged_url = path + '?' + query_string if query_string else path
        merged_urls.append(merged_url)

    return merged_urls, js_urls


######## Get The Output ########
def get_result_urls(domain):
    wayback_urls = get_url_from_wayback(domain)
    commoncrawl_urls = get_urls_from_commoncrawl(domain)
    
    
    all_urls = wayback_urls + commoncrawl_urls
    unique_urls = list(set(all_urls))

    return unique_urls
