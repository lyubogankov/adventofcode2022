import math

import solution
from solution import Sensor, CoordPair

def visualize_sensor_beacon_map(sensors, show_excl_sensor_coords=[], highlight_x=None, highlight_y=None):
    # finding boundary of coordinate grid
    smallest_x, smallest_y, largest_x, largest_y = solution.calculate_map_bounds(sensors, show_excl_sensor_coords)
    # create output string
    mapstr = ""
    for y in range(smallest_y, largest_y + 1):
        for x in range(smallest_x, largest_x + 1):
            current = CoordPair(x, y)
            if any(current == s.coords for s in sensors):
                mapstr += 'S'
            elif any(current == s.nearest_beacon_coords for s in sensors):
                mapstr += 'B'
            elif any(s.coords in show_excl_sensor_coords and s.is_within_exclusion_zone(current) for s in sensors):
                mapstr += '#'
            else:
                mapstr += '.'
        if y in highlight_y:
            mapstr += ' ***'
        if y != largest_y:
            mapstr += '\n'
    if highlight_x:
        highlight_x_str = ""
        for x in range(smallest_x, largest_x + 1):
            highlight_x_str += "*" if x in highlight_x else " "
        mapstr += '\n' + highlight_x_str + '\n' + highlight_x_str
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
    print(visualize_sensor_beacon_map(sensors, sensor_coords, highlight_x=[0, 20], highlight_y=[0, 20]))