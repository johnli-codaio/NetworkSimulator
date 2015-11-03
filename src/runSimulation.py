import argparse
import json
import pprint

def main():
    parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name', 
                        help = 'Store JSON file name')
    args = parser.parse_args()

    f = open(args.json_file_name) 

    data = json.load(f)

    pprint.pprint(data)


if __name__ == "__main__":
    main()


