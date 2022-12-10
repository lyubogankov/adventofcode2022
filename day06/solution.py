from collections import deque

def process_datastream_and_find_first_n_consecutive_unique_characters(datastream, n):
    last_n_chars = deque(maxlen=n)
    index = 0
    for char in datastream:
        index += 1
        last_n_chars.append(char)
        if len(last_n_chars) < n:
            continue
        if len(set(last_n_chars)) == n:
            return index

def part_one__find_first_packet_start_marker(datastream):
    return process_datastream_and_find_first_n_consecutive_unique_characters(datastream, n=4)

def part_two__find_first_message_start_marker(datastream):
    return process_datastream_and_find_first_n_consecutive_unique_characters(datastream, n=14)

if __name__ == '__main__':
    filelist = [f'example_{i}.txt' for i in range(1, 6)] + ['input.txt']
    for datastream_buffer_file in filelist:
        with open(datastream_buffer_file) as datastream:
            d = datastream.read()
            first_packet_start_marker = part_one__find_first_packet_start_marker(d)
            first_message_start_marker = part_two__find_first_message_start_marker(d)
            print(f'[{datastream_buffer_file:^13}] packet: {first_packet_start_marker:>4}  message: {first_message_start_marker:>4}')