import math

import solution
from solution import Sensor, CoordPair, BoundingBox

BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

def visualize_sensor_beacon_map(sensors, show_excl_sensor_coords=[], highlight_x=[], highlight_y=[], boundingbox: BoundingBox=None, square_coords=False):
    # finding boundary of coordinate grid
    smallest_x, smallest_y, largest_x, largest_y = solution.calculate_map_bounds(sensors, show_excl_sensor_coords)
    # if we want to visualize the map in square-coords, need to perform conversions here.
    if square_coords:
        # The map bounding box is itself in diamond coords, but is a square.
        # Need to calculate the smallest diamond that fits the diamond-coords map bounding box.
        bounding_diamond_center = CoordPair(
            x = smallest_x + (largest_x - smallest_x)/2,
            y = smallest_y + (largest_y - smallest_y)/2
        )
        bounding_diamond_radius = max(abs(largest_x - smallest_x), abs(largest_y - smallest_y))
        # now, convert to equivalent square bounding box and expand to map limits
        (smallest_x, smallest_y), (largest_x, largest_y) = \
            solution.diamond_to_square(bounding_diamond_center, bounding_diamond_radius)
        # ensure the list of sensor coords is in the square coord system
        show_excl_sensor_coords = [solution.diamond_to_square_coords(c) for c in show_excl_sensor_coords]
        # the highlighting of rows/cols doesn't make sense since we've rotated by 45deg
        highlight_y = []
        highlight_x = []
    # create output string
    mapstr = ""
    for y in range(smallest_y, largest_y + 1):
        for x in range(smallest_x, largest_x + 1):
            current = CoordPair(x, y)
            # color the next character if it's part of the boundingbox edge
            color = RED if boundingbox and boundingbox.edge_contains(current, square_coords) else None
            if color:
                mapstr += color
            # decide on the next character
            if any(current == eval(f"s.{'s_' if square_coords else ''}coords") for s in sensors):
                mapstr += 'S'
            elif any(current == eval(f"s.{'s_' if square_coords else ''}nearest_beacon_coords") for s in sensors):
                mapstr += 'B'
            elif any(eval(f"s.{'s_' if square_coords else ''}coords") in show_excl_sensor_coords and s.is_within_exclusion_zone(current, square_coords) for s in sensors):
                mapstr += '#'
            else:
                mapstr += '.'
            # if we used a color, reset
            if color:
                mapstr += RESET
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

    # print(visualize_sensor_beacon_map(sensors, sensor_coords, highlight_x=[0, 20], highlight_y=[0, 20], square_coords=True))
    
    print(
        visualize_sensor_beacon_map(
            sensors, sensor_coords, 
            highlight_x=[0, 20], highlight_y=[0, 20], 
            boundingbox=BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(20, 20))   
        )
    )

    print(
        visualize_sensor_beacon_map(
            sensors, sensor_coords,
            boundingbox=BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(20, 20)),
            square_coords=True
        )
    )