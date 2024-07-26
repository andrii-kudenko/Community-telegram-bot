from geopy.geocoders import Nominatim
def get_location(latitude, longitude):
    geolocator = Nominatim(user_agent="andrew")
    location = geolocator.reverse((latitude, longitude), language='en')
    address = location.raw['address']
    road = address.get('road', 'Unknown')
    city = address.get('city', 'Unknown')
    country = address.get('country', 'Unknown')
    return (road, city, country)
