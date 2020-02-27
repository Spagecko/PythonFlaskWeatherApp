from uszipcode import SearchEngine

#searches zip code base on city and state 
def getZipcode(city,state):
    search = SearchEngine()
    zipSearch = search.by_city_and_state(city, state)
    zipcode = zipSearch[0]
    zipcode = zipcode.zipcode

    return zipcode

