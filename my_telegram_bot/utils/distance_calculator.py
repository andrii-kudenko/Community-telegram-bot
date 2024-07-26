import math

def great_circle_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg):
    # Convert degrees to radians
    lat1_rad = math.radians(lat1_deg)
    lon1_rad = math.radians(lon1_deg)
    lat2_rad = math.radians(lat2_deg)
    lon2_rad = math.radians(lon2_deg)
    
    # Calculate the distance using the formula
    distance = math.acos(
        math.sin(lat1_rad) * math.sin(lat2_rad) +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad)
    ) * 6371 * 1.2
    
    return distance

# Example coordinates 
# Location 1
lat1 = 43.46815
lon1 = -79.69735
# Location 2
lat2 = 43.48301
lon2 = -79.71833

distance = great_circle_distance(lat1, lon1, lat2, lon2)
print(f"The great-circle distance is: {distance} km")