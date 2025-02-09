import os
import sys

def check_data(dir_path):
    data = {}
    files = os.listdir(dir_path)
    for file_name in files:
        if file_name.endswith('.result'):
            result = {}
            try:
                with open(os.path.join(dir_path, file_name), 'r') as f:
                    lines = f.readlines()
                    result['coins'] = int(lines[0].split(': ')[1])
                    result['fractals'] = int(lines[1].split(': ')[1])
                    result['run_coins'] = int(lines[2].split(': ')[1])
                    result['submit_fractal'] = float(lines[3].split(': ')[1])
                    result['accept_fractal'] = float(lines[4].split(': ')[1].replace('%', ''))
                    result['invalid_accept_fractal'] = int(lines[5].split(': ')[1])
                    result['valid_reject_fractal'] = int(lines[6].split(': ')[1])
                    result['coin_satisfaction'] = float(lines[7].split(': ')[1].replace('%', ''))
                    result['trader_satisfaction'] = float(lines[8].split(': ')[1].replace('%', ''))
                    result['average_adjacency'] = float(lines[9].split(': ')[1])
                    result['max_adjacency'] = int(lines[10].split(': ')[1])
                    result['max_cooperation'] = int(lines[11].split(': ')[1])

                data[file_name.split('.')[0]] = result
            except:
                print(f'Error reading file {file_name}')

if __name__ == '__main__':
    # Check the number of arguments
    if len(sys.argv) != 3:
        print('Usage: python check-data.py <directory_path> <linear_directory_path>')
        sys.exit(1)

    # Load the data
    print('Data loading...')
    check_data(sys.argv[1])
    print('= ' * 20)
    print('Linear data loading...')
    check_data(sys.argv[2])