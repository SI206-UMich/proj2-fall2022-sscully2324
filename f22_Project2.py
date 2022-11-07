from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest


def get_listings_from_search_results(html_file):

    #open the file
    f = open(html_file, 'r')
    #read the file
    html = f.read()
    #close the file
    f.close()
    #parse the file
    soup = BeautifulSoup(html, 'html.parser')
    #find the listing title
    listing_title = soup.find_all('div', class_ = 't1jojoys dir dir-ltr')
    #find the cost
    cost = soup.find_all('span', class_ = '_tyxjp1')
    #find the digits after /rooms/ in the listing id only 
    listing_id = soup.find_all('a', class_ = 'ln2bl2p dir dir-ltr')
    #get the digits after /rooms/ in the listing id only, with no brackets
    for i in range(len(listing_id)):
        listing_id[i] = re.findall(r'\d+', listing_id[i]['href'])
    #get the listing title, cost, and listing id in a list of tuples
    listing_info = []
    for i in range(len(listing_title)):
        listing_info.append((listing_title[i].text, int(cost[i].text.strip('$')), listing_id[i][0]))
    return listing_info



def get_listing_information(listing_id):

    f = open('html_files/' + "listing_" + listing_id + '.html', 'r')
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, 'html.parser')

    #get the policy number
    policy_number = soup.find('li', class_ = 'f19phm7j dir dir-ltr')
    policy_number = re.findall(r'STR-\d+|2022-\d+STR|Pending|pending|Exempt', policy_number.text)
    if policy_number == []:
        policy_number = 'Exempt'
    elif 'pending' in policy_number or 'Pending' in policy_number:
        policy_number = 'Pending'
    else:
        policy_number = policy_number[0]

    #get the place type
    place_type = soup.find('h2', class_ = '_14i3z6h')
    place_type = re.findall(r'Private room|Shared room', place_type.text)
    if place_type == []:
        place_type = 'Entire Room'
    else:
        
        place_type = place_type[0].title()

    #get the number of bedrooms
    num_bedrooms = soup.find('span', string = re.compile(r'[S|s]tudio|[B|b]edroom'))
    num_bedrooms = re.findall(r'\d+', num_bedrooms.text)
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
    """
    Write a function that takes in a list of tuples (called data, i.e. the
    one that is returned by get_detailed_listing_database()), sorts the tuples in
    ascending order by cost, writes the data to a csv file, and saves it
    to the passed filename. The first row of the csv should contain
    "Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms",
    respectively as column headers. For each tuple in data, write a new
    row to the csv, placing each element of the tuple in the correct column.

    When you are done your CSV file should look like this:

    Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    title1,cost1,id1,policy_number1,place_type1,num_bedrooms1
    title2,cost2,id2,policy_number2,place_type2,num_bedrooms2
    title3,cost3,id3,policy_number3,place_type3,num_bedrooms3
    ...

    In order of least cost to most cost.

    This function should not return anything.
    """
    pass


def check_policy_numbers(data):
    """
    Write a function that takes in a list of tuples called data, (i.e. the one that is returned by
    get_detailed_listing_database()), and parses through the policy number of each, validating the
    policy number matches the policy number format. Ignore any pending or exempt listings.
    Return the listing numbers with respective policy numbers that do not match the correct format.
        Policy numbers are a reference to the business license San Francisco requires to operate a
        short-term rental. These come in two forms, where # is a number from [0-9]:
            20##-00####STR
            STR-000####
    .
    Return value should look like this:
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """
    pass


def extra_credit(listing_id):
    """
    There are few exceptions to the requirement of listers obtaining licenses
    before listing their property for short term leases. One specific exception
    is if the lister rents the room for less than 90 days of a year.

    Write a function that takes in a listing id, scrapes the 'reviews' page
    of the listing id for the months and years of each review (you can find two examples
    in the html_files folder), and counts the number of reviews the apartment had each year.
    If for any year, the number of reviews is greater than 90 (assuming very generously that
    every reviewer only stayed for one day), return False, indicating the lister has
    gone over their 90 day limit, else return True, indicating the lister has
    never gone over their limit.
    """
    pass


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

        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1

        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2

        pass

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string

        # check that the element in the list is a string

        # check that the first element in the list is '16204265'
        pass


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)
