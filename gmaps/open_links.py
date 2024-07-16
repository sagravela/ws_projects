import csv
import webbrowser
import argparse

def open_links():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Open links from a CSV file')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('-n', type=int, default=10, help='Number of links to open')
    args = parser.parse_args()
    # Read the CSV file and extract the links
    links = []
    with open(args.csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            link = row.get('link')
            if link:  # Check if the link is not empty
                links.append(link)
            if i == args.n - 1:
                break

    print(links)
    # Open each link in the default browser
    for link in links:
        webbrowser.open(link)


if __name__ == '__main__':
    open_links()