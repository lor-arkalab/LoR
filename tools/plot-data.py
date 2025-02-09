import os
import sys
import numpy as np
from PIL import Image
from matplotlib import cm
from typing import DefaultDict
import matplotlib.pyplot as plt

FIG_SIZE=(10,7)
FONT_SIZE=18

def trim_image(file_name):
    # Load image and convert to numpy array
    image = Image.open(file_name)
    image_data = np.asarray(image)

    # Find the non-white pixels
    non_white = np.where(image_data != 255)
    x_min, x_max = non_white[0].min(), non_white[0].max() + 1
    y_min, y_max = non_white[1].min(), non_white[1].max() + 1

    # Crop the image and save it
    image_data = image_data[x_min:x_max, y_min:y_max]
    image = Image.fromarray(image_data)
    image.save(file_name)

def plot_3d_data(data, title, z_label, save_as=None):
    # Create a meshgrid for the 3D plot
    X, Y = np.meshgrid(np.arange(0, 101, 5), np.arange(0, 101, 5))

    # Flatten the grid to use with bar3d
    x_pos = X.flatten()
    y_pos = Y.flatten()
    z_pos = np.zeros_like(x_pos)  # All bars start at z=0

    # Bar dimensions
    dx = dy = 5  # Each bar will represent 5% intervals
    dz = np.transpose(data).flatten()

    # Gradient color based on the alpha
    gradient_values = np.where(x_pos + y_pos > 100, 0, x_pos / 10 + y_pos)
    gradient_values -= gradient_values.min()
    gradient_values = gradient_values / gradient_values.max()

    # Define the colormap and set the colors
    colors = cm.coolwarm(gradient_values)
    colors[np.where(x_pos + y_pos > 100)] = 0

    # Create the figure and 3D axis
    fig = plt.figure(figsize=FIG_SIZE)
    ax = fig.add_subplot(111, projection='3d')

    # Create the 3D bar plot
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, color=colors, shade=True)

    # Set axis labels
    ax.set_xlabel(r'$\beta$ (%)', fontsize=FONT_SIZE)
    ax.set_ylabel(r'$\alpha$ (%)', fontsize=FONT_SIZE)
    ax.set_zlabel(z_label, fontsize=16, rotation=90)

    # Set ticks for better readability
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_yticks(np.arange(0, 101, 10))

    # Set initial view
    ax.zaxis.set_rotate_label(False)
    ax.view_init(elev=30, azim=-20)

    # Save the plot if a file name is provided
    if save_as:
        plt.savefig(save_as)
        trim_image(save_as)

    # Set title
    ax.set_title(title, fontsize=FONT_SIZE)

    # Show the plot
    plt.show()

def sparse_data(data, k=1, indexes=None):
    if indexes is None:
        indexes = np.arange(len(data))
    sparsed_data = np.zeros_like(data)
    for i, index1 in enumerate(indexes):
        total, factor = 0, 0
        for index2, data2 in zip(indexes, data):
            total += data2 * np.exp(k * -abs(index1 - index2))
            factor += np.exp(k * -abs(index1 - index2))
        sparsed_data[i] = total / factor
    return sparsed_data

def plot_2d_data(data, title, y_label, fit_degree=3, save_as=None):
    FONT_SIZE=20
    # Process the data and find different alpha percentages
    alpha_percentages = np.sort([alpha for alpha in data.keys() if len(data[alpha]) > 0])
    data = [np.mean(data[alpha]) for alpha in alpha_percentages]
    data = sparse_data(data, indexes=alpha_percentages)

    # Fit a polynomial to the data
    z = np.polyfit(alpha_percentages, data, fit_degree)
    fitted_data = np.poly1d(z)(alpha_percentages)

    # Gradient color based on the alpha
    gradient_values = np.where(alpha_percentages > 100, 0, alpha_percentages)
    gradient_values -= gradient_values.min()
    gradient_values = gradient_values / gradient_values.max()

    # Define the colormap and set the colors
    colors = cm.coolwarm(gradient_values)

    # Create the figure and axis
    fig = plt.figure(figsize=FIG_SIZE)
    ax = fig.add_subplot(111)

    # Plot the data with a gradient color
    for i in range(len(alpha_percentages) - 1):
        ax.plot(alpha_percentages[i:i+2], data[i:i+2], '-', color=colors[i])

    # Plot the fitted data
    ax.plot(alpha_percentages, fitted_data, '--', color='purple')

    # Set axis labels
    ax.set_xlabel(r'$\gamma$ (%)', fontsize=FONT_SIZE)
    ax.set_ylabel(y_label, fontsize=FONT_SIZE)

    # Save the plot if a file name is provided
    if save_as:
        plt.savefig(save_as)
        trim_image(save_as)

    # Set title
    ax.set_title(title, fontsize=FONT_SIZE)

    # Show the plot
    plt.show()

    # Return the fitted data for further analysis
    return alpha_percentages, fitted_data

def plot_scenarios(data_bad, data_random, data_p, fitted_data, title, y_label, save_as=None):
    FONT_SIZE=22
    # Get the keys and values of the linear data
    p_keys = np.sort(list(data_p.keys()))
    p_values = np.array([data_p[key] for key in p_keys])
    bad_keys = np.sort(list(data_bad.keys()))
    bad_values = np.array([data_bad[key] for key in bad_keys])
    random_keys = np.sort(list(data_random.keys()))
    random_values = np.array([data_random[key] for key in random_keys])

    # Create the figure and axis
    fig = plt.figure(figsize=FIG_SIZE)
    ax = fig.add_subplot(111)

    # Plot the data
    ax.plot(fitted_data[0], fitted_data[1], '--', color='purple', label=r'Reliablity Level ($\gamma$)')
    ax.plot([-5, 105], [data[0][0], data[0][0]], '--', color='green', label=r'Honest Behavior ($\alpha=\beta=0$)')
    ax.plot(bad_keys, sparse_data(bad_values), '-', color='red', label=r'Bad Behavior ($\alpha$)')
    ax.plot(random_keys, sparse_data(random_values), '-', color=r'orange', label=r'Random Behavior ($\beta$)')
    ax.plot(p_keys, sparse_data(p_values), '-', color='blue', label=r'Maliciously Probability ($p$)')

    # Set axis labels
    ax.set_xlabel('Amount (%)', fontsize=FONT_SIZE)
    ax.set_ylabel(y_label, fontsize=FONT_SIZE)
    handles, labels = ax.get_legend_handles_labels()
    order = [0, 2, 3, 4, 1]
    ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], fontsize=13)

    # Save the plot if a file name is provided
    if save_as:
        plt.savefig(save_as)
        trim_image(save_as)
    
    # Set title
    ax.set_title(title, fontsize=FONT_SIZE)

    # Show the plot
    plt.show()

def load_data(dir_path):
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
    return data

if __name__ == '__main__':
    # Check the number of arguments
    if len(sys.argv) != 3:
        print('Usage: python3 plot-data.py <directory_path> <linear_directory_path>')
        sys.exit(1)

    # Load the data
    raw_data = load_data(sys.argv[1])
    raw_linear_data = load_data(sys.argv[2])

    # Plot percentage of invalid accepted fractal rings
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['invalid_accept_fractal'] / raw_data[file_name]['fractals'] * 100
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['invalid_accept_fractal'] / raw_linear_data[file_name]['fractals'] * 100
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['invalid_accept_fractal'] / raw_linear_data[file_name]['fractals'] * 100
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['invalid_accept_fractal'] / raw_linear_data[file_name]['fractals'] * 100
    plot_3d_data(data_2d, 'Percentage of Invalid Accepted Fractal Rings', 'Invalid Accepted Fractal Rings (%)', save_as='images/invalid-accepted.png')
    fitted_data = plot_2d_data(data, 'Percentage of Invalid Accepted Fractal Rings', 'Invalid Accepted Fractal Rings (%)', 12, 'images/invalid-accepted-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Percentage of Invalid Accepted Fractal Rings', 'Invalid Accepted Fractal Rings (%)', 'images/invalid-accepted-scenario.png')

    # Plot percentage of valid rejected fractal rings
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['valid_reject_fractal'] / raw_data[file_name]['fractals'] * 100
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['valid_reject_fractal'] / raw_linear_data[file_name]['fractals'] * 100
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['valid_reject_fractal'] / raw_linear_data[file_name]['fractals'] * 100
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['valid_reject_fractal'] / raw_linear_data[file_name]['fractals'] * 100
    plot_3d_data(data_2d, 'Percentage of Valid Rejected Fractal Rings', 'Valid Rejected Fractal Rings (%)', save_as='images/valid-rejected.png')
    fitted_data = plot_2d_data(data, 'Percentage of Valid Rejected Fractal Rings', 'Valid Rejected Fractal Rings (%)', 12, 'images/valid-rejected-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Percentage of Valid Rejected Fractal Rings', 'Valid Rejected Fractal Rings (%)', 'images/valid-rejected-scenario.png')

    # Average adjacency per trader
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['average_adjacency']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['average_adjacency']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['average_adjacency']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['average_adjacency']
    plot_3d_data(data_2d, 'Average Number of Communication Complexity', 'Average No. of Communications', save_as='images/average-communication.png')
    fitted_data = plot_2d_data(data, 'Average Number of Communication Complexity', 'Average No. of Communications', 5, 'images/average-communication-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Average Number of Communication Complexity', 'Average No. of Communications', 'images/average-communication-scenario.png')

    # Maximum adjacency per trader
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['max_adjacency']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['max_adjacency']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['max_adjacency']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['max_adjacency']
    plot_3d_data(data_2d, 'Maximum Number of Communication Complexity', 'Max No. of Communications', save_as='images/maximum-communication.png')
    fitted_data = plot_2d_data(data, 'Maximum Number of Communication Complexity', 'Max No. of Communications', 5, save_as='images/maximum-communication-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Maximum Number of Communication Complexity', 'Max No. of Communications', 'images/maximum-communication-scenario.png')

    # Average fractal ring acceptance rate per trader
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['accept_fractal']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['accept_fractal']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['accept_fractal']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['accept_fractal']
    plot_3d_data(data_2d, 'Average Fractal Ring Acceptance Rate', 'Fractal Ring Acceptance Rate (%)', save_as='images/fractal-acceptance.png')
    fitted_data = plot_2d_data(data, 'Average Fractal Ring Acceptance Rate', 'Fractal Ring Acceptance Rate (%)', 7, 'images/fractal-acceptance-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Average Fractal Ring Acceptance Rate', 'Fractal Ring Acceptance Rate (%)', 'images/fractal-acceptance-scenario.png')

    # Average satisfaction per coin
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['coin_satisfaction']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['coin_satisfaction']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['coin_satisfaction']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['coin_satisfaction']
    plot_3d_data(data_2d, 'Average Coin Satisfaction', 'Coin Satisfaction (%)', save_as='images/coin-satisfaction.png')
    fitted_data = plot_2d_data(data, 'Average Coin Satisfaction', 'Coin Satisfaction (%)', 12, 'images/coin-satisfaction-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Average Coin Satisfaction', 'Coin Satisfaction (%)', 'images/coin-satisfaction-scenario.png')

    # Average satisfaction per trader
    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['trader_satisfaction']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['trader_satisfaction']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['trader_satisfaction']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['trader_satisfaction']
    plot_3d_data(data_2d, 'Average Trader Satisfaction', 'Trader Satisfaction (%)', save_as='images/trader-satisfaction.png')
    fitted_data = plot_2d_data(data, 'Average Trader Satisfaction', 'Trader Satisfaction (%)', 12, 'images/trader-satisfaction-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Average Trader Satisfaction', 'Trader Satisfaction (%)', 'images/trader-satisfaction-scenario.png')

    data, data_2d = DefaultDict(list), np.zeros((21, 21))
    data_bad, data_random, data_p = {}, {}, {}
    for i in range(21):
        for j in range(21):
            file_name = f'{i*5}-{j*5}'
            if file_name in raw_data:
                value = raw_data[file_name]['max_cooperation']
                data_2d[i][j], data[i / 2 + j * 5] = value, np.append(data[i / 2 + j * 5], value)
    for file_name in raw_linear_data:
        if file_name.endswith('-p'):
            data_p[int(file_name[:-2])] = raw_linear_data[file_name]['max_cooperation']
        elif file_name.endswith('-num-bad'):
            data_bad[int(file_name[:-8])] = raw_linear_data[file_name]['max_cooperation']
        elif file_name.endswith('-num-random'):
            data_random[int(file_name[:-11])] = raw_linear_data[file_name]['max_cooperation']
    plot_3d_data(data_2d, 'Maximum Cooperation', r'$\ell$ (Maximum Cooperation)', 'images/max-cooperation.png')
    fitted_data = plot_2d_data(data, 'Maximum Cooperation', r'$\ell$ (Maximum Cooperation)', 5, 'images/max-cooperation-2d.png')
    plot_scenarios(data_bad, data_random, data_p, fitted_data, 'Maximum Cooperation', r'$\ell$ (Maximum Cooperation)', 'images/max-cooperation-scenario.png')