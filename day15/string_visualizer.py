import math

import solution
from solution import Sensor, CoordPair

def visualize_sensor_beacon_map(sensors, show_excl_sensor_coords=[]):
    # finding boundary of coordinate grid
    smallest_x = smallest_y = math.inf
    largest_x = largest_y = -math.inf
    for s in sensors:
        smallest_x = min(smallest_x, s.coords.x, s.nearest_beacon_coords.x, s.coords.x - s.radius if s.coords in show_excl_sensor_coords else  math.inf)
        smallest_y = min(smallest_y, s.coords.y, s.nearest_beacon_coords.y, s.coords.y - s.radius if s.coords in show_excl_sensor_coords else  math.inf)
        largest_x  = max(largest_x,  s.coords.x, s.nearest_beacon_coords.x, s.coords.x + s.radius if s.coords in show_excl_sensor_coords else -math.inf)
        largest_y  = max(largest_y,  s.coords.y, s.nearest_beacon_coords.y, s.coords.y + s.radius if s.coords in show_excl_sensor_coords else -math.inf)
    # create output string
    mapstr = ""
    for y in range(smallest_y, largest_y + 1):
        for x in range(smallest_x, largest_x + 1):
            current = CoordPair(x, y)
            for s in sensors:
                if current == s.coords:
                    mapstr += 'S'
                    break
                elif current == s.nearest_beacon_coords:
                    mapstr += 'B'
                    break
                elif s.coords in show_excl_sensor_coords and s.is_within_exclusion_zone(current):
                    mapstr += '#'
                    break
            else:
                mapstr += '.'
        if y != largest_y:
            mapstr += '\n'
    return mapstr

if __name__ == '__main__':
    ## visualizing just the board
    # print(visualize_sensor_beacon_map(inputfile='example.txt'))

    ## visualizing single sensor's exclusion area
    # print(visualize_sensor_beacon_map(
    #     sensors=solution.parse_input_file_into_sensors_and_beacons(inputfile='example.txt'),
    #     show_excl_sensor_coords=[CoordPair(8, 7)]
    # ))

    ## visualizing all sensors' exclusion areas
    sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile='example.txt')
    sensor_coords = [s.coords for s in sensors]
    print(visualize_sensor_beacon_map(sensors, sensor_coords))