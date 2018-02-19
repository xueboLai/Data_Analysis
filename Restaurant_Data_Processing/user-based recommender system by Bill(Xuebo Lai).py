from __future__ import print_function
from django.utils.encoding import smart_str
import argparse
import json
import pprint
import requests
import sys
import urllib
import time
from random import *
import urllib.request
import codecs
import math

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except:
    print("somehting is worng with the import")

CLIENT_ID = "wCwISBTyESR56y0Z2eu3qQ"
CLIENT_SECRET = "sdiRHX4R3XlJwMeQOd3ZzQEaH6GF4xN782MfKp0i6EbubXbFCVKz3T6J4yKUKw5n"

#major link
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

#this is the list for default; increase the fault tolerance for the whole program
DEFAULT_TERM = 'restaurant'
DEFAULT_LOCATION = 'Manhattan,NY'
SEARCH_LIMIT = 5
OFFSET = 0
x=50
radius = 5
price = "1,2,3,4"
attributes = "N/A"
latitude = 0
longitude = 0
#input_categories = []
categor = ""


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token

def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    #print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search(bearer_token, term, location):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    if(attributes!="N/A"):
        if(latitude==0):
            url_params = {
                'term': term.replace(' ', '+'),
                'location': location.replace(' ', '+'),
                'limit': SEARCH_LIMIT,
                #"offset": OFFSET,
                "radius_filter": radius,
                "price": price,
                #"attributes": attributes,
                "category_filter":categor,
                "sort":1
                }
        else:
            url_params = {
                'term': term.replace(' ', '+'),
                #'latitude': latitude,
                #'longitude': longitude,
                'limit': SEARCH_LIMIT,
                #'offset': OFFSET,
                "radius_filter": radius,
                "price": price,
                #"attributes": attributes,
                "category_filter":categor,
                "sort":1
                }
    else:
        if(latitude==0):
            url_params = {
                'term': term.replace(' ', '+'),
                'location': location.replace(' ', '+'),
                'limit': SEARCH_LIMIT,
                #"offset": OFFSET,
                "radius_filter": radius,
                "price": price,
                #"attributes": attributes,
                "category_filter":categor,
                "sort":1
                }
        else:
            url_params = {
                'term': term.replace(' ', '+'),
                #"latitude": latitude,
                #"longitude": longitude,
                'limit': SEARCH_LIMIT,
                #"offset": OFFSET,
                "radius_filter": radius,
                "price": price,
                #"attributes": attributes,
                "category_filter":categor,
                "sort":1
                }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)

def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    response = search(bearer_token, term, location)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    r1 = []
    for i in range(len(businesses)):
        business_id = businesses[i]['id']
        r1.append(get_business(bearer_token, business_id))
        
    business_id = businesses[0]['id']

    #print(u'{0} businesses found, querying business info ' \
    #    'for the top result "{1}" ...'.format(
    #        len(businesses), business_id))
    response = get_business(bearer_token, business_id)
    
    #print(u'Result for business "{0}" found:'.format(business_id))
    #pprint.pprint(response, indent=2)
    return r1

def travel_time(origin,destination,travel_mode):
    reader = codecs.getreader("utf-8")
    #all defined here is fixed for the url
    origin_final = "origins="+origin+"&"
    destination_final = "destinations="+destination+"&"
    key = "key=AIzaSyDV-aAQfBxSi4Emh0j6UWaqf-tbBrqhSIs"
    prefix = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    if(travel_mode=="w"):
        mode ="mode=walking&"
    elif(travel_mode=="d"):
        mode="mode=driving&"
    elif(travel_mode=="p"):
        mode = "mode=transit&"
    else:
        mode = "mode=bicycling&"
    #wpd
    depart_time = "departure_time=now&"
    lang = "language=en&"
    merge = prefix+origin_final+destination_final+mode+depart_time+lang+key
    #print("\n\n\n\n\ni'm here\n\n\n")
    print(merge)
    answer = json.load(reader(urllib.request.urlopen(merge)))
    #print(answer["rows"][0]['elements'][0]["duration"]["value"])
    return int(answer["rows"][0]['elements'][0]["duration"]["value"])

class user:
    def __init__(self,name,double_lst,label):
        self.name = name
        self.double_lst = double_lst
        self.label = label

    #getter
    def getDoubleList(self):
        return self.double_lst
    def getLabel(self):
        return self.label
    def getName(self):
        return self.name


class newUser:
    def __init__(self,name,double_lst):
        self.double_lst = double_lst
        self.name= name

    #getter
    def getDoubleList(self):
        return self.double_lst

    def getName(self):
        return self.name

def sortByTime(lst):
    #sorted(AllRestaurants,key=lambda restaurant: restaurant.getTime())
    for i in range((len(lst)-1)):
        minValue = lst[i]
        minIndex = i
        for j in range(i,len(lst)):
            if(lst[j].getTime()<lst[minIndex].getTime()):
                minValue = lst[j]
                minIndex = j
        temp = lst[i]
        lst[i] = lst[minIndex]
        lst[minIndex] = temp
    return lst

#    def getRating(self): sorted by price
def sortByRating(lst):
    #sorted(AllRestaurants,key=lambda restaurant: restaurant.getTime())
    for i in range((len(lst)-1)):
        minValue = lst[i]
        minIndex = i
        for j in range(i,len(lst)):
            if(lst[j].getRating()<lst[minIndex].getRating()):
                minValue = lst[j]
                minIndex = j
        temp = lst[i]
        lst[i] = lst[minIndex]
        lst[minIndex] = temp
    return lst

#def getPrice(self):


def sortByPrice(lst):
    #sorted(AllRestaurants,key=lambda restaurant: restaurant.getTime())
    for i in range((len(lst)-1)):
        minValue = lst[i]
        minIndex = i
        for j in range(i,len(lst)):
            if(lst[j].getPrice()<lst[minIndex].getPrice()):
                minValue = lst[j]
                minIndex = j
        temp = lst[i]
        lst[i] = lst[minIndex]
        lst[minIndex] = temp
    return lst




class restaurant:
    def __init__(self,name,address,phone,categories,is_closed,price, rating,review_count,myLocation,travel_mode):
        self.name = name
        self.address = address
        self.phone = phone
        self.categories = categories
        self.closed = is_closed
        self.price = price
        self.rating = rating
        self.review_count = review_count
        self.travelTime = travel_time(address,myLocation,travel_mode)

    def __cmp__(self,obj):
        if(self.travelTime-obj.getTime()>0):
            return 1
        elif(self.travelTime-obj.getTime()<0):
            return -1
        else:
            return 0
    #getter
    def getTime(self):
        return int(self.travelTime)
    def getName(self):
        return self.name
    def getAddress(self):
        return self.address
    def getPhone(self):
        return str(self.phone)
    def getCategories(self):
        return self.categories
    def getClosed(self):
        return str(self.closed)
    def getPrice(self):
        return str(self.price)
    def getRating(self):
        return str(self.rating)
    def getReviewCount(self):
        return str(self.review_count)



def read_file(inputFile,m):
    try:
        inFile = open(inputFile,m)
    except:
        print("There's something wrong with printing the file "+inputFile)
        exit(1)
    return inFile

def Eulidean(lst1,lst2):
    if(len(lst1)!=len(lst2)):
        print(lst1)
        print(lst2)
        print(len(lst1))
        print(len(lst2))
        print("length error of Eulidean Distance, terminated")
        exit(1)
    summ = 0.0
    for i in range(len(lst1)):
        summ+=((lst1[i]-lst2[i])*(lst1[i]-lst2[i]))*1.0
    result = math.sqrt((summ*1.0))
    return result
        

def Knn(inputFile,newDataItem):
    print("searching for result1")
    #skip the first line
    inputFile.readline()
    #create a list holding on to all the cluster
    allCluster = []
    #input the first cluster
    line = inputFile.readline()
    line.split(",")
    line_lst = line.split(",")
    name = line_lst[0]
    cluster = line_lst[1]
    double_lst = []
    for i in range(len(line_lst)):
        if(i>1 and i!=(len(line_lst)-1)):
            double_lst.append(float(line_lst[i]))
        elif(i==(len(line_lst)-1)):
            lst = line_lst[i].split("\\")
            double_lst.append(float(lst[0]))
    oneUser = user(name,double_lst,cluster)
    oneCluster = []
    allCluster.append(oneCluster)
    allCluster[0].append(oneUser)
    existed_cluster = False
    print("searching for result2")
    for line in inputFile:
        line_lst = line.split(",")
        name = line_lst[0]
        cluster = line_lst[1]
        double_lst = []
        for i in range(len(line_lst)):
            if(i>1 and i!=(len(line_lst)-1)):
                double_lst.append(float(line_lst[i]))
            elif(i==(len(line_lst)-1)):
                lst = line_lst[i].split("\\")
                double_lst.append(float(lst[0]))
        user1 = user(name,double_lst,cluster)
        print("The line is "+line+", next is gonna be cheking clustering")
        for j in allCluster:
            print("Processing data, performing k-nn, please be patient")
            for z in j:
                print("Processing data, performing k-nn, please be patient")
                if(z.getLabel()==user1.getLabel()):
                    existed_cluster = True
                    j.append(user1)
                    print("K-cluster found, continuing")
                    break
            if(existed_cluster==False):
                oneCluster = []
                allCluster.append(oneCluster)
                allCluster[(len(allCluster)-1)].append(user1)
                print("New Cluster has been created")
            
    score = []
    print("searching for result3")
    for aCluster in allCluster:
        sumup = 0
        for aUser in aCluster:
            sumup+=Eulidean(aUser.getDoubleList(),newDataItem.getDoubleList())
        average_Eulidean = (sumup*1.0/(1.0*len(aCluster)))
        score.append(average_Eulidean)
    min_index = score.index(min(score))
    allcategories = []
    print("searching for result4")
    for oneUser in allCluster[min_index]:
        Allcategory = oneUser.getDoubleList()
        for a in range(len(Allcategory)):
            if(Allcategory[a]!=0):
                try:
                    test = allcategories.index(a)
                except:
                    allcategories.append(a)
    return allcategories
                    

'''
    def getDoubleList(self):
        return self.double_lst
    def getLabel(self):
        return self.label
    def getName(self):
        return self.name
'''
#class user:
#    def __int__(self,double_lst,label): 
    
        
    
    

def main():
    newUserFile = read_file("newUser.csv","a")
    stringBuilder = ""
    name = input("Hello! Welcome to use our app. \nPlease share with us your name\n")
    #address_type = input("Please enter g or s to indicate whether you want to enter geocoordinates or street name\n")
    stringBuilder += (name+",")
    address_type = "s"
    stringBuilder += (address_type+",")
    address = input("Please input your address\n")
    stringBuilder += (address+",")
    budget = float(input("Please share with us your budget\n"))
    stringBuilder += (str(budget)+",")
    way_to_get_to_restaurnat = input("Please share with us your preferred way to get to the restaurant: w(walking), p(public transit),d(driving),b(bycycling)\n")
    stringBuilder += (str(way_to_get_to_restaurnat)+",")
    maximum_time = int(input("Please share with us your the maximum time (in second) that you are willing to spend to restaurant\n"))
    stringBuilder += (str(maximum_time)+",")
    number_of_restaurants = int(input("please input the restaurant's number you want to view\n"))
    stringBuilder += (str(number_of_restaurants)+",")
    vegetarian = input("are you a vegetarian? yes or no\n")
    stringBuilder += (str(vegetarian)+",")
    sortingWay = input("Please input how you want to see the output: best rating on the top(r), highest price on the top(hp), lowest price on the top(lp), travel time to the restaurant:low to high(t)\n")
    stringBuilder += (str(sortingWay)+",")
    print("In order to make our prediction more accurate, please provide your rating for the category or restaurant below(scale 0-5;5 is the best, 0 is really bad or no common)\n")


#    if(travel_mode=="w"):
#        mode ="mode=walking&"
#    elif(travel_mode=="d"):
#        mode="mode=driving&"
#    elif(travel_mode=="p"):
#        mode = "mode=transit&"
#    else:
#        mode = "mode=bicycling&"

    
    c0 = int(input("Fields Good Chicken(American_food):"))
    c1 = int(input("International Wings Factory(American_traditional):"))
    c2 = int(input("Saigon Shack(Asian soup and noodle):"))
    c3 = int(0)
    c4 = 0
    c5 = int(input("Daily Provisions(cafe):"))
    c6 = 0
    c7 = int(input("Margon (cuban):"))
    c8 = 0
    c9 = 0
    c10 = int(input("San Marzano Pasta Fresca (Italian)"))
    c11 = int(input("Quan Sushi(Japanese)"))
    c12 = int(input("Eva's Kitchen(Juice Bars & Smoothies)"))
    c13 = int(input("Korilla BBQ (Korean)"))
    c14 = 0
    c15 = int(input("La Goulette (Mediterranean):"))
    c16 = int(input("Chipotle (Mexican)"))
    c17 = int(input("Joe's Pizza(pizza)"))
    c18 = 0
    c19 = int(input("The PokéSpot (seafood)"))
    c20 = 0
    c21 = int(input("Soho Thai (Thai)"))
    c22 = int(input("by CHLOE (Vegan)"))
    print("Thanks for your patience; here's the result:")
    double_list = [c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22]
    for anything in double_list:
        stringBuilder += (str(anything)+",")
    newUserFile.write(stringBuilder)
    newUserFile.close()
    aNewUser = newUser(name,double_list)
    inputFile = read_file("/Users/xuebolai/Downloads/User_Ratings_MEAN_usable.csv","r")
    preferred_categories = Knn(inputFile,aNewUser)
    print(preferred_categories)

    lstOfCategory = ["American_new","American_traditional","Asian","Bars","Brunch","Cafe","Chinese","Cuban","French","Indian","Italian","Japanese","Juice Bars","Korean","Latin","Mediterranean","Mexican","Pizza","Ramen","Seafood","Spanish","Thai","Vegetarian"]

    
  
    
    #c9 = int(input(""))
    #k-nn output, a list of all the users in the cluster that the new user is in, list of categories(in number) that all users in the cluster like.

    global OFFSET
    global SEARCH_LIMIT
    global radius
    global input_categories
    global price
    global latitude
    global longitude
    global categor
    categor = ""
    for i in preferred_categories:
        categor += lstOfCategory[i]+","
    print("The categor is "+categor)
    categor = categor[:-2]
    OFFSET = 0
    SEARCH_LIMIT = number_of_restaurants
    CorL = ""
    if(address_type=="g"):
        CorL = "c"
    else:
        CorL = "l"
        
    if(CorL=="c"):
        cor_list = address.split(",")
        latitude = cor_list[0]
        longitude = cor_list[1]
    else:
        address = address.replace(" ","+")
        print("address is "+address)
        DEFAULT_LOCATION = address
    
    if(budget<=10):
        price = "1"
    elif(budget>10 and budget<=20):
        price = "1,2"
    elif(budget>=20 and budget<=30):
        price = "1,2,3"
    else:
        price = "1,2,3,4"
    if(vegetarian=="yes"):
        attributes = "vegetarian"

    #the program can later be used to take in argument
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        response = query_api(input_values.term, input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )
    restaurants = []
    file_output = open("output_yelp.csv","a")
    print(response)
    AllRestaurants = []
    for i in response:
            #encoded_name = i["name"].encode("utf-8")
        name = i["name"]
        try:
            file_output.write(name+",")
        except:
            file_output.write("foreign_name"+",")
            #print(i["location"])
            #file_output.write(i["location"]["coordinate"]["latitude"]+",")
            #file_output.write(i["location"]["coordinate"]["longitude"]+",")
        file_output.write(i["location"]["zip_code"]+",")
        city = i["location"]["city"]
        file_output.write(i["location"]["city"]+",")
        file_output.write(i["location"]["state"]+",")
        rest_address = ""
        for address1 in i["location"]["display_address"]:
            rest_address +=(address1.replace(" ","+")+"+")
            file_output.write(address1.replace(",","_")+"_")
        rest_address =rest_address.replace("++","+")
        rest_address = rest_address.replace(",","")
        rest_address = rest_address[:-1]
            
        file_output.write(",")
        phone = i["display_phone"]
        file_output.write(i["display_phone"]+",")
        rest_categories = ""
        for kind in i["categories"]:
            rest_categories+=kind["alias"]+";"
            file_output.write(kind["alias"]+";")
            #print(i["categories"])
            #file_output.write(i["categories"][0]["alias"]+",")
        rest_categories = rest_categories[:-2]
        file_output.write(",")
        #    file_output.write(str(response["coordinates"]["latitude"])+"|"+str(response["coordinates"]["longitude"]+","))
        try:
            file_output.write(i["id"]+",")
        except:
                file_output.write("error id"+",")
        file_output.write(str(i["is_closed"])+",")
        is_closed = i["is_closed"]
        file_output.write(i["price"]+",")
        price = i["price"]
        file_output.write(str(i["rating"])+",")
        rating = i["rating"]
        file_output.write(str(i["review_count"])+"\n")
        number_of_rating = i["review_count"]
        print("rest_address: "+rest_address)
        print("regular address"+address)
        aRest = restaurant(name,rest_address,phone,rest_categories,is_closed,price,rating,number_of_rating,address,way_to_get_to_restaurnat)
        AllRestaurants.append(aRest)
        file_output.write("\n")
    file_output.close()
    #AllRestaurants = sorted(AllRestaurants,key=lambda restaurant: restaurant.getTime())

    #sortingWay = input("Please input how you want to see the output: best rating on the top(r), highest price on the top(hp), lowest price on the top(lp), travel time to the restaurant:low to high(t)")

    if(sortingWay=="r"):
        AllRestaurants = sortByRating(AllRestaurants)
    elif(sortingWay=="hp"):
        AllRestaurants = sortByPrice(AllRestaurants)
        AllRestaurants.reverse()
    elif(sortingWay=="lp"):
        AllRestaurants = sortByPrice(AllRestaurants)
    else:
        AllRestaurants = sortByTime(AllRestaurants)
    AllRestaurants_tmp = AllRestaurants
    AllRestaurants = []
    for anItem in AllRestaurants_tmp:
        if (anItem.getTime()<=maximum_time):
            AllRestaurants.append(anItem)
            
    #sorted(student_objects, key=lambda student: student.age)


    print("\n\n\n")
    print("recommended restaurants' list:("+str(len(restaurants))+" restaurants)")
    for i in AllRestaurants:
        print("restaurant: ")
        print("Name："+i.getName())
        print("Location: "+(i.getAddress().replace("+"," ")))
        print("It takes "+str(i.getTime())+" seconds to get there")
        print("phone number: "+str(i.getPhone()))
        print("categories: "+i.getCategories())
        print("closed? "+str(i.getClosed()))
        print("price range:"+i.getPrice())
        print("rating: "+str(i.getRating())+" out of 5.0")
        print("The rating is based on "+str(i.getReviewCount())+" people")
        print("\n\n")







'''
        AllRestaurants.append(aRest)
        file_output.write("\n")
    file_output.close()
    sorted(AllRestaurants)

    print("recommended restaurants' list:"+str(len(restaurants)))
    for i in AllRestaurants:
        print("restaurant: ")
        print("Name："+i.getName())
        print("Location: "+getAddress())
        print("It takes "+i.travelTime()+"to get there")
        print("phone number: "+i.getPhone())
        print("categories"+i.getCategories())
        print("closed? "+i.getClosed())
        print("price range:"+i.getPrice())
        print("rating: "+i.getRating())
        print("The rating is based on "+i.getReviewCount())
        print("\n\n")
    



    def getTime(self):
        return str(self.travelTime)
    def getName(self):
        return self.name
    def getAddress(self):
        return self.address
    def getPhone(self):
        return str(self.phone)
    def getCategories(self):
        return self.categories
    def getClosed(self):
        return str(self.closed)
    def getPrice(self):
        return str(self.price)
    def getRating(self):
        return str(self.rating)
    def getReviewCount(self):
        return str(self.review_count)
    def travelTime(self):
        return str(self.travelTime)

'''

     

'''
    try:
        for i in response:
            name = i["name"]
            try:
                file_output.write(name+",")
            except:
                file_output.write("foreign_name"+",")
            #print(i["location"])
            #file_output.write(i["location"]["coordinate"]["latitude"]+",")
            #file_output.write(i["location"]["coordinate"]["longitude"]+",")
            file_output.write(i["location"]["zip_code"]+",")
            city = i["location"]["city"]
            file_output.write(city+",")
            file_output.write(i["location"]["state"]+",")
            rest_address = ""
            for raddress in i["location"]["display_address"]:
                file_output.write(raddress.replace(",","_")+"_")
                rest_address = (rest_adress+raddress.replace(",","_")+"_")
            rest_address = rest_address[:-2]
            file_output.write(",")
            phone = i["display_phone"]
            file_output.write(phone+",")
            categories = ""
            for kind in i["categories"]:
                categories = categories+kind["alias"]+";"
                file_output.write(kind["alias"]+";")
            file_output.write(",")
        #    file_output.write(str(response["coordinates"]["latitude"])+"|"+str(response["coordinates"]["longitude"]+","))
            try:
                file_output.write(i["id"]+",")
            except:
                file_output.write("error id"+",")
            is_closed = str(i["is_closed"])
            file_output.write(str(i["is_closed"])+",")
            file_output.write(i["price"]+",")
            price_range = i["price"]
            file_output.write(str(i["rating"])+",")
            rating = str(i["rating"])
            file_output.write(str(i["review_count"])+"\n")
            number_of_rating = i["review_count"]
            aRest = restaurant(name,rest_address,phone,categories,is_closed,price,rating,number_of_rating,address)
            print(name+","+rest_address+"\n\n")
            restaurants.append(aRest)
#class restaurant:
#def __init__(self,name,address,phone,categories,is_closed,price, rating,review_count,myLocation):
        file_output.write("\n")
        file_output.close()
    except:
        file_output.write("\n")
        file_output.close()
    sorted(restaurants)

    print("recommended restaurants' list:"+str(len(restaurants)))
    for i in restaurants:

        print("restaurant: ")
        print("Name："+i.getName())
        print("Location: "+getAddress())
        print("It takes "+i.getTime()+"to get there")
        print("phone number: "+i.getPhone())
        print("categories"+i.getCategories())
        print("closed? "+i.getClosed())
        print("price range:"+i.getPrice())
        print("rating: "+i.getRating())
        print("The rating is based on "+i.getReviewCount())
        print("\n\n")
        
        
if __name__ == '__main__':
    while(True):
        main()
'''
main()




 
