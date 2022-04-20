from bs4 import BeautifulSoup
import requests
import csv
import time


def get_company_contact(company_card):
    try:
        company_page = requests.get(company_card.h3.a['href'])
    except:
        company_page = requests.get(clutch_url + company_card.h3.a['href'], headers=headers)

    soup_company_page = BeautifulSoup(company_page.content, 'lxml')
    try:
        contact_number = soup_company_page.find('section', class_='quick-menu active provider-row').find('li',
                                                                                                         class_='quick-menu-details').a[
                             'href'][4:]

    except:
        return "Not Provided"

    company_page.close()
    contact_number = contact_number.replace("%29", ")")
    contact_number = contact_number.replace("%28", "(")
    contact_number = contact_number.replace("%20", " ")
    if '.' in contact_number:
        contact_number = ' '.join(contact_number.split("."))
    elif contact_number == '-':
        contact_number = 'Not Provided'

    return contact_number


def get_company_project_size(company_card):
    try:
        return company_card.find('div', class_='list-item block_tag custom_popover').text.strip()
    except:
        return 'Not Provided'


def get_company_hourly_rate(company_card):
    try:
        return ''.join(company_card.find('div', class_='list-item custom_popover').span.text.strip().split(" "))
    except:
        return 'Not Provided'


def get_company_review_count(company_card):
    try:
        return company_card.find('a', class_='reviews-link sg-rating__reviews').text.strip().split(" ")[0]
    except:
        return 'Not Provided'


def get_company_ratings(company_card):
    try:
        return company_card.find('span', class_='rating sg-rating__number').text.strip()
    except AttributeError:
        return "Not Provided"


def get_company_url(company_card):
    try:
        return "/".join(company_card.find('div', class_='provider-detail col-md-2').a['href'].split('/')[:3])
    except:
        return 'Not Provided'


def get_company_name(company_card):
    try:
        return company_card.h3.a.text.strip()
    except:
        return 'Not Provided'


def get_company_location(company_card):
    try:
        return company_card.find('span', class_='locality').text
    except:
        return 'Not Provided'


def get_company_employee_size(company_card):
    try:
        return ''.join(company_card.find_all('div', class_='list-item custom_popover')[1].span.text.strip().split(" "))
    except:
        return 'Not Provided'


clutch_url = 'https://clutch.co'

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.79 Safari/537.36 '
}

main_page = requests.get(clutch_url, headers=headers)
soup = BeautifulSoup(main_page.content, 'lxml')
sitemap_wrapper = soup.find('div', class_="sitemap-wrapper")
all_domains_tags = sitemap_wrapper.find_all('a', class_='sitemap-nav__item')
all_domains = {all_domains_tags[i].text.strip():clutch_url + all_domains_tags[i]['href'] for i in range(len(all_domains_tags))}

for i in range(len(all_domains.keys())):
    print( f"{i+1}) {list(all_domains.keys())[i]}" )
selection = int(input("Select a number: "))


url = f'{all_domains[list(all_domains.keys())[selection-1]]}'  # General Url for selected Page
page = requests.get(url, headers=headers)   # Requesting page information
soup = BeautifulSoup(page.content, 'lxml')  # Parsing page content using lxml parser

page_limit = soup.find_all('a', class_='page-link')[-1]['data-page']

file = open('Clutch.csv', 'w',encoding="utf-8")
writer = csv.writer(file)
writer.writerow(['Company', 'Website', 'Location', 'Contact', 'Rating', 'Review Count', 'Hourly Rate', 'Min Project Size', 'Employee Size'])

# Finding number of pages for pagination

for i in range(int(page_limit)):     # Iteration for each page

    url = f'{url}?page={i}'   # Page for number i
    while True:
        try:
            page = requests.get(url, headers=headers)   # Requesting page information
            break
        except requests.exceptions.ConnectionError:
            time.sleep(5)

    soup = BeautifulSoup(page.content, 'lxml')  # Parsing page content using lxml parser
    page.close()
    companies_row = soup.find('ul', class_='directory-list shortlist')    # Row containing all company's company_card
    company_cards = companies_row.find_all('li', class_='provider provider-row sponsor')    # Filtering out each company card
    company_cards_nonsponsor = companies_row.find_all('li', class_='provider provider-row') # Filtering out each company card
    company_cards.extend(company_cards_nonsponsor)  # Final List of all company cards

    for j in range(len(company_cards)-1):
        row_data = []

        company_name = get_company_name(company_cards[j])                          #    Get Company Name
        row_data.append(company_name)                                              #    Append to Row List

        company_url = get_company_url(company_cards[j])                            #    Get Company Website Url
        row_data.append(company_url)                                               #    Append to Row List

        company_location = get_company_location(company_cards[j])                  #    Get Company Location
        row_data.append(company_location)                                          #    Append to Row List

        company_contact = get_company_contact(company_cards[j])                    #    Get Company Contact info
        row_data.append(company_contact)                                           #    Append to Row List

        company_ratings = get_company_ratings(company_cards[j])                    #    Get Company Ratings
        row_data.append(company_ratings)                                           #    Append to Row List

        company_review_count = get_company_review_count(company_cards[j])          #    Get Company Review Count
        row_data.append(company_review_count)                                      #    Append to Row List

        company_hourly_rate = get_company_hourly_rate(company_cards[j])            #    Get Company Hourly Rate
        row_data.append(company_hourly_rate)                                       #    Append to Row List

        company_project_size = get_company_project_size(company_cards[j])          #    Get Company Project Size
        row_data.append(company_project_size)                                      #    Append to Row List

        company_employee_size = get_company_employee_size(company_cards[j])        #    Get Company Employee Size
        row_data.append(company_employee_size)                                     #    Append to Row List

        writer.writerow(row_data)

file.close()
