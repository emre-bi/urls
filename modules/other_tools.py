import subprocess
import sys
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_to_http(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == "https":
        parsed_url = parsed_url._replace(scheme="http")
    return urlunparse(parsed_url)



#### Run Hakrawler (urls from source code) ####
def run_hakrawler(subdomain):
    try:
        logger.info(f"Running Hakrawler: {subdomain}")
        subdomain_netloc = urlparse(subdomain).netloc
        command = ['hakrawler', '-d', '100']
        result = subprocess.run(
            command,
            input=subdomain,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.stdout:
            urls = result.stdout.splitlines()
        else:
            print(result.stderr)
            return []
        
        url_of_the_domain = []
        for url in urls:
            url_netloc = urlparse(url).netloc
            if url_netloc == subdomain_netloc:
                url_of_the_domain.append(url)

        return url_of_the_domain
    except Exception as e:
        print(f"Error running Hakrawler : {e}")
    

#### Run Katana (urls from source code) ####
def run_katana(subdomain):
    try:
        logger.info(f"Running Katana: {subdomain}")
        subdomain_netloc = urlparse(subdomain).netloc

        command = ['katana', '-u', subdomain, '-d', '100']
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.stdout:
            urls = result.stdout.splitlines()
        else:
            print(result.stderr)
            return []
        
        url_of_the_domain = []
        for url in urls:
            url_netloc = urlparse(url).netloc
            if url_netloc == subdomain_netloc:
                url_of_the_domain.append(url)

        return url_of_the_domain
    except Exception as e:
        print(f"Error running Katana : {e}")


#### Run GAU (historic urls)####
def run_gau(subdomain):
    try:
        logger.info(f"Running Gau: {subdomain}")
        subdomain_netloc = urlparse(subdomain).netloc

        command = ['gau']
        result = subprocess.run(
            command,
            input=subdomain,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.stdout:
            urls = result.stdout.splitlines()
        else:
            print(result.stderr)
            return []
        
        url_of_the_domain = []
        for url in urls:
            url_netloc = urlparse(url).netloc
            if url_netloc == subdomain_netloc:
                url_of_the_domain.append(url)

        return url_of_the_domain
    except Exception as e:
        print(f"Error running Katana : {e}")


#### Run getJS to get .js files ####
def run_getJS(subdomain):
    try:
        logger.info(f"Running getJS: {subdomain}")
        subdomain_netloc = urlparse(subdomain).netloc

        command = ['getJS', '--url', subdomain]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stdout:
            urls = result.stdout.splitlines()
        else:
            print(result.stderr)
            return []
        
        url_of_the_domain = []
        for url in urls:
            url_netloc = urlparse(url).netloc
            if subdomain_netloc in url_netloc:
                url_of_the_domain.append(url)

        return url_of_the_domain
    except Exception as e:
        print(f"Error running getJS : {e}")


def get_other_urls(domain):
    hakrawler_urls = run_hakrawler(domain)
    katana_urls = run_katana(domain)
    gau_urls = run_gau(domain)
    getjs_urls = run_getJS(domain)

    all_urls = hakrawler_urls + katana_urls + getjs_urls + gau_urls
    unique_urls = list(set(all_urls))

    return unique_urls



if __name__ == "__main__":
    subdomain = "localhost:5000"

    if not (subdomain.startswith("http://") or subdomain.startswith("https://")):
        subdomain = "http://" + subdomain
    
    urls = run_linkfinder(subdomain)
    for url in urls:
        print(url)
