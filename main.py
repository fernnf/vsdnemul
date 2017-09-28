import argparse
import json
from pprint import pprint

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("-t","--topology",type = argparse.FileType('r'), help = "json file with topology load")
    args = parse.parse_args()

    with open(args.topology.name) as topo:
        d = json.load(topo)

        pprint(d['nodes'][0])


