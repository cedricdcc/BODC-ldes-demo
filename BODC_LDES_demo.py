# python test file that will do sparql query to an endpoint of BODC

import requests
import urllib.parse
import json
import sys
import os
import datetime

# define constants

ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"
WD = os.path.dirname(os.path.realpath(__file__))
QUERY = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX skosc: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?id ?sid ?version ?modified WHERE {
        ?id rdf:type skosc:Concept .
        ?id dcterms:identifier ?sid .
        ?id dcterms:date ?modified .
        ?id <http://purl.org/pav/hasCurrentVersion> ?version
    }
    ORDER BY DESC(?modified)
    LIMIT 1500
    """

# demo url http://vocab.nerc.ac.uk/sparql/sparql?query={YOUR_QUERY_URL_ENCODED}

def get_triples(query:str):
    """
    Get triples from the endpoint
    """
    
    # make sure the query is url endcoded
    encoded_query = urllib.parse.quote(query)
    
    params = {
        "Accept": "application/sparql-results+json"
    }
    URL = ENDPOINT + "?query=" + encoded_query
    response = requests.get(URL, params=params)
    if response.status_code != 200:
        print("Error: SPARQL query failed")
        print(response.text)
        sys.exit(1)
    return response.json()

'''
print("Querying the endpoint...")
results = get_triples(QUERY)
print("Got {} results.".format(len(results["results"]["bindings"])))
print("Writing to file...")



with open(os.path.join(WD,"BODC_LDES_demo.json"), "w") as f:
    json.dump(results["results"]["bindings"], f, indent=4)

r_array = results["results"]["bindings"] if results else None
'''

with open(os.path.join(WD,"BODC_LDES_demo.json"), "r") as f:
    # read in the file
    r_array = json.load(f)

# print(r_array)
        
# split up the result array so that the content is sorted by day
# if no results are found for a day, the day will not be included in the array

# get the first date
first_date = r_array[0]["modified"]["value"].split("T")[0]
print(first_date)

# round the first date to the nearest day in the future
closest_end_date = datetime.datetime.strptime(first_date, "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(hours=1)
closest_begin_date = datetime.datetime.strptime(first_date, "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=1)

print(closest_begin_date), print(closest_end_date)

# take the last element of the array and do the same
last_date = r_array[-1]["modified"]["value"].split("T")[0]
print(last_date)

furthest_end_date = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(hours=1)
furthest_begin_date = datetime.datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=1)

print(furthest_begin_date), print(furthest_end_date)

# make an array of all the dates in between the first and last date per hour
date_array = []
date_array.append(closest_begin_date)
while date_array[-1] > furthest_end_date:
    date_array.append(date_array[-1] - datetime.timedelta(hours=1))
date_array.pop(-1)
date_array.append(furthest_begin_date)
print(len(date_array))

# loop through the date array and find the results that match the date
# if no results are found, then the date is skipped
# if results are found, then the results are added to the array
# the array is then added to the json file
# the json file is then written to a file

# create a new array to store the results
new_array = []

# loop through the date array
for date in date_array:
    next_date = date - datetime.timedelta(hours=1)
    following_date = date - datetime.timedelta(hours=2)
    # print(date)
    # print(next_date)
    # create a new array to store the results for that date
    date_results = []
    # loop through the results array
    date_bigger = True
    result_found = False
    for result in r_array:
        
        if date_bigger == True:
            # check if the date is smaller then the current date but larger then the next date if it exists
            if datetime.datetime.strptime(result["modified"]["value"].split("T")[0], "%Y-%m-%d %H:%M:%S.%f") < date and datetime.datetime.strptime(result["modified"]["value"].split("T")[0], "%Y-%m-%d %H:%M:%S.%f") > next_date:
                # add the result to the date results array
                date_results.append(result)
                r_array.remove(result)
                result_found = True
            else:
                if result_found:
                    date_bigger = False
                    print(len(r_array))
    # add the date results array to the new array
    if len(date_results) > 0:
        date_str = str(next_date)+ "-" + str(date)
        # convert str to uri compatible
        date_str_uri = urllib.parse.quote(date_str)
        previous_date = str(following_date) + "-" + str(next_date)
        previous_date_uri = urllib.parse.quote(previous_date)
        new_array.append({"date": date_str_uri,"results":date_results, "previous_date": previous_date_uri})
        print(len(date_results))

print(len(new_array))

# write array to file as json
with open(os.path.join(WD,"BODC_LDES_demo_sorted.json"), "w") as f:
    json.dump(new_array, f, indent=4)

# execute the following command 
# delete the metadata.ttl file if it exists
# python -m pysubyt -t ./pysubyt -s qres BODC_LDES_demo_sorted.json -n metadata.ttl -o metadata.ttl
if os.path.exists(os.path.join(WD,"metadata.ttl")):
    os.remove(os.path.join(WD,"metadata.ttl"))

os.system("python -m pysubyt -t ./pysubyt -s qres BODC_LDES_demo_sorted.json -n metadata.ttl -o metadata.ttl")




