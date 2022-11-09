#Name: Sean Scully
#UMID: 51027244
#People I worked with: Annabelle Phillips, Brooke Rossow


from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest


def get_listings_from_search_results(html_file):

    f = open(html_file, 'r')
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    listing_title = soup.find_all('div', class_ = 't1jojoys dir dir-ltr')
    cost = soup.find_all('span', class_ = '_tyxjp1')
    listing_id = soup.find_all('a', class_ = 'ln2bl2p dir dir-ltr')
    for i in range(len(listing_id)):
        listing_id[i] = re.findall(r'\d+', listing_id[i]['href'])
    listing_info = []
    for i in range(len(listing_title)):
        listing_info.append((listing_title[i].text, int(cost[i].text.strip('$')), listing_id[i][0]))
    return listing_info


def get_listing_information(listing_id):

    f = open('html_files/' + "listing_" + listing_id + '.html', 'r')
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')
    policy_number = soup.find('li', class_ = 'f19phm7j dir dir-ltr')
    policy_number = re.findall(r'(?:STR)?(?:\d+)?-?\d+(?:STR)?|[Pp]ending', policy_number.text)
    if policy_number == []:
        policy_number = 'Exempt'
    elif 'pending' in policy_number or 'Pending' in policy_number:
        policy_number = 'Pending'
    else:
        policy_number = policy_number[0]
    place_type = soup.find('h2', class_ = '_14i3z6h')
    place_type = re.findall(r'[Pp]rivate room?|[Ss]hared room?', place_type.text)
    if place_type == []:
        place_type = 'Entire Room'
    else:
        place_type = place_type[0].title()
    num_bedrooms = soup.find('span', string = re.compile(r'[S|s]tudio|[B|b]edroom'))
    num_bedrooms = re.findall(r'\d+\s', num_bedrooms.text)
    if num_bedrooms == []:
        num_bedrooms = 1
    else:
        num_bedrooms = int(num_bedrooms[0])
    listing_info = (policy_number, place_type, num_bedrooms)
    return listing_info


def get_detailed_listing_database(html_file):

    listings = get_listings_from_search_results(html_file)
    detailed_listings = []
    for listing in listings:
        detailed_listing = (listing[0], listing[1], listing[2]) + get_listing_information(listing[2])
        detailed_listings.append(detailed_listing)
    return detailed_listings


def write_csv(data, filename):

    data.sort(key = lambda x: x[1])
    with open(filename, 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms'])
        for i in range(len(data)):
            writer.writerow(data[i])
    return None

    
def check_policy_numbers(data):

    policy_number = []
    for i in range(len(data)):
        policy_number.append(data[i][3])  
    listing_id = []
    for i in range(len(data)):
        listing_id.append(data[i][2])
    index = []
    for i in range(len(policy_number)):
        if not re.match(r'20\d{2}-00\d{4}STR|STR-000\d{4}', policy_number[i]) and policy_number[i] != 'Pending' and policy_number[i] != 'Exempt':
            index.append(i)
    wrong_id = []
    for i in index:
        wrong_id.append(listing_id[i])
    return wrong_id


def extra_credit(listing_id):

    f = open('html_files/' + "listing_" + listing_id + '_reviews.html', 'r')
    file = f.read()
    f.close()
    soup = BeautifulSoup(file, 'html.parser')
    review_dates = soup.find_all('li', class_ = '_1f1oir5')
    year = []
    for i in range(len(review_dates)):
        year.append(re.findall(r'\d{4}', review_dates[i].text))
    year_count = {}
    for i in range(len(year)):
        if year[i][0] in year_count:
            year_count[year[i][0]] += 1
        else:
            year_count[year[i][0]] = 1
    for i in year_count:
        if year_count[i] > 90:
            return False
    return True


class TestCases(unittest.TestCase):


    def test_get_listings_from_search_results(self):

        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        self.assertEqual(len(listings), 20)
        self.assertEqual(type(listings), list)
        for item in listings:
            self.assertEqual(type(item), tuple)
        self.assertEqual(listings[0], ('Loft in Mission District', 210, '1944564'))
        self.assertEqual(listings[-1], ('Guest suite in Mission District', 238, '32871760'))


    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        listing_informations = [get_listing_information(id) for id in html_list]
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            self.assertEqual(type(listing_information), tuple)
            self.assertEqual(len(listing_information), 3)
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            self.assertEqual(type(listing_information[2]), int)
        self.assertEqual(listing_informations[0][0], 'STR-0001541')
        self.assertEqual(listing_informations[-1][1], 'Private Room')
        self.assertEqual(listing_informations[2][2], 1)


    def test_get_detailed_listing_database(self):

        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            self.assertEqual(type(item), tuple)
            self.assertEqual(len(item), 6)
        self.assertEqual(detailed_database[0], ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))
        self.assertEqual(detailed_database[-1], ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1))


    def test_write_csv(self):

        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        write_csv(detailed_database, "test.csv")
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        self.assertEqual(len(csv_lines), 21)
        self.assertEqual(csv_lines[0], ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms'])
        self.assertEqual(csv_lines[1], ['Private room in Mission District', '82', '51027324', 'Pending', 'Private Room', '1'])
        self.assertEqual(csv_lines[-1], ['Apartment in Mission District', '399', '28668414', 'Pending', 'Entire Room', '2'])


    def test_check_policy_numbers(self):

        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        invalid_listings = check_policy_numbers(detailed_database)
        self.assertEqual(type(invalid_listings), list)
        self.assertEqual(len(invalid_listings), 1)
        self.assertEqual(type(invalid_listings[0]), str)
        self.assertEqual(invalid_listings[0], '16204265')


    def test_extra_credit(self):
        self.assertEqual(extra_credit("16204265"), False)
        self.assertEqual(extra_credit("1944564"), True)


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)