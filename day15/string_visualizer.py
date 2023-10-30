import math

import solution
from solution import Sensor, CoordPair

def visualize_sensor_beacon_map(inputfile: str):
    sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile)
    # finding boundary of coordinate grid
    smallest_x = smallest_y = math.inf
    largest_x = largest_y = -math.inf
    for s in sensors:
        smallest_x = min(smallest_x, s.coords.x, s.nearest_beacon_coords.x)
        smallest_y = min(smallest_y, s.coords.y, s.nearest_beacon_coords.y)
        largest_x  = max(largest_x,  s.coords.x, s.nearest_beacon_coords.x)
        largest_y  = max(largest_y,  s.coords.y, s.nearest_beacon_coords.y)    
    # create output string
    mapstr = ""
    for y in range(smallest_y, largest_y + 1):
        for x in range(smallest_x, largest_x + 1):
            for s in sensors:
                if CoordPair(x, y) == s.coords:
                    mapstr += 'S'
                    break
                elif CoordPair(x, y) == s.nearest_beacon_coords:
                    mapstr += 'B'
                    break
            else:
                mapstr += '.'
        if y != largest_y:
            mapstr += '\n'
    return mapstr

if __name__ == '__main__':
    print(visualize_sensor_beacon_map(inputfile='example.txt'))