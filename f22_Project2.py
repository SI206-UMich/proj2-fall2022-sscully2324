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
    policy_number = re.findall(r'(?:STR)?(?:\d+)?-?\d+(?:STR)?|Pending|pending|Exempt|exempt', policy_number.text)
    if policy_number == []:
        policy_number = 'Exempt'
    elif 'pending' in policy_number or 'Pending' in policy_number:
        policy_number = 'Pending'
    else:
        policy_number = policy_number[0]
    place_type = soup.find('h2', class_ = '_14i3z6h')
    place_type = re.findall(r'Private room|Shared room', place_type.text)
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


class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings), 20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        for item in listings:
            self.assertEqual(type(item), tuple)
        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)
        self.assertEqual(listings[0], ('Loft in Mission District', 210, '1944564'))
        # check that the last title is correct (open the search results html and find it)
        self.assertEqual(listings[-1], ('Guest suite in Mission District', 238, '32871760'))


    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has policy number 'STR-0001541'
        self.assertEqual(listing_informations[0][0], 'STR-0001541')
        # check that the last listing in the html_list is a "Private Room"
        self.assertEqual(listing_informations[-1][1], 'Private Room')
        # check that the third listing has one bedroom
        self.assertEqual(listing_informations[2][2], 1)


    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)
        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1
        self.assertEqual(detailed_database[0], ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))
        # check that the last tuple is made up of the following:
        # 'Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1
        self.assertEqual(detailed_database[-1], ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1))


    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)
        # check that the header row is correct
        self.assertEqual(csv_lines[0], ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms'])
        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1
        self.assertEqual(csv_lines[1], ['Private room in Mission District', '82', '51027324', 'Pending', 'Private Room', '1'])
        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2
        self.assertEqual(csv_lines[-1], ['Apartment in Mission District', '399', '28668414', 'Pending', 'Entire Room', '2'])


    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string
        self.assertEqual(len(invalid_listings), 1)
        # check that the element in the list is a string
        self.assertEqual(type(invalid_listings[0]), str)
        # check that the first element in the list is '16204265'
        self.assertEqual(invalid_listings[0], '16204265')


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)