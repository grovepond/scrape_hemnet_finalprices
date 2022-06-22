import requests
import argparse
import re
import csv
from bs4 import BeautifulSoup
from requests_html import HTMLSession

parser = argparse.ArgumentParser()

#-o OUTPUT -u URL
parser.add_argument("-o", "--output", help="Output CSV file", type=str, default='output.csv')
parser.add_argument("-u", "--url", help="Search URL",
                    default='https://www.hemnet.se/salda/bostader?housing_form_groups%5B%5D=houses&location_ids%5B%5D=18015&sold_age=12m',
                    type=str)
args = parser.parse_args()


def get_and_print_content (soup, page):
    alt = ''
    mode = 'w'
    if (page > 1):
        mode = 'a'
    ul = soup.find('ul', class_='sold-results')
    lines = ul.find_all('li', class_='sold-results__normal-hit')
        
    
    for line in lines:
        price_change = line.find('div', class_='sold-property-listing__price-change')
        if (hasattr(price_change, 'text')):
            percent = price_change.text
            final_price = line.find('div', class_='sold-property-listing__price').find('div', class_='sold-property-listing__subheading')
            if (hasattr(final_price, 'text')):
                final_price_value = final_price.text
            footer = line.find('div', class_='sold-property-listing__footer')
            if (hasattr(footer, 'find')):
                broker = footer.find('div', class_='sold-property-listing__broker-logo')
                broker_name = broker.find('img')
                alt = broker_name.get('alt')
            data = [alt, re.sub('[^a-zA-Z0-9\n\.]', '', final_price_value.replace('kr', '').replace(' ', '').replace('Slutpris', '').strip()), percent.replace('%', '').replace('+', '').replace('±', '').strip(), alt]
            writer.writerow(data)
    return

session = HTMLSession()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64; rv:91.0) Gecko/20100101 Firefox/91.0',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive'}
base_url = args.url
base_url = base_url + '&page='
page_number = 1

with open(args.output, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Broker', 'Final Price', 'Percent'])
    
    # Loop for pagination
    while True:
        url = base_url + str(page_number)
        r = session.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        if (soup.find('div', class_='next_page pagination__item pagination__item--disabled')):
            break
        elif 'alla' in (soup.find('div', class_='result-pagination').find('p').find('b').text):
           break
        get_and_print_content(soup, page_number)
        page_number += 1    


print ('Successfully saved to ' + args.output)
exit
