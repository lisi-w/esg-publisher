import esgcet.update as up
import os
import sys
import json
import argparse
import configparser as cfg
from pathlib import path

def get_args():
    parser = argparse.ArgumentParser(description="Publish data sets to ESGF databases.")

    home = str(Path.home())
    def_config = home + "/.esg/esg.ini"
    parser.add_argument("--index-node", dest="index_node", default=None, help="Specify index node.")
    parser.add_argument("--certificate", "-c", dest="cert", default="./cert.pem",
                        help="Use the following certificate file in .pem form for publishing (use a myproxy login to generate).")
    parser.add_argument("--pub-rec", dest="json_data", required=True,
                        help="JSON file output from esgpidcitepub or esgmkpubrec.")
    parser.add_argument("--ini", "-i", dest="cfg", default=def_config, help="Path to config file.")

    pub = parser.parse_args()

    return pub


def run():
    a = get_args()

    ini_file = a.cfg
    config = cfg.ConfigParser()
    config.read(ini_file)

    try:
        s = config['user']['silent']
        if 'true' in s or 'yes' in s:
            silent = True
        else:
            silent = False
    except:
        silent = False

    try:
        v = config['user']['silent']
        if 'true' in v or 'yes' in v:
            verbose = True
        else:
            verbose = False
    except:
        verbose = False

    if a.cert == "./cert.pem":
        try:
            cert = config['user']['cert']
        except:
            cert = a.cert
    else:
        cert = a.cert

    if a.index_node is None:
        try:
            index_node = config['user']['index_node']
        except:
            print("Index node not defined. Use the --index-node option or define in esg.ini.", file=sys.stderr)
            exit(1)
    else:
        index_node = a.index_node

    try:
        new_json_data = json.load(open(a.json_data))
    except:
        print("Error opening json file. Exiting.", file=sys.stderr)
        exit(1)

    try:
        up.run([new_json_data, index_node, cert, silent, verbose])
    except Exception as ex:
        print("Error updating: " + str(ex), file=sys.stderr)
        exit(1)


def main():
    run()


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    main()
