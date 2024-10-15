from joblib import cpu_count
from structure import Structure
import argparse
import os

def parse_args():
    # get args
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--path', help='Path of Pictures', type=str, required=True)
    parser.add_argument('-e','--extensions', help='Extensions of pictures', type=str, required=True)
    parser.add_argument('-r','--raw-extensions', help='Extensions of raw pictures', type=str, required=True)
    parser.add_argument('-c','--cores', help='Number of cores', type=int, default=int(cpu_count()), required=False)
    args = parser.parse_args()
    # clean args
    args.path = os.path.realpath(os.path.expanduser(args.path))
    args.extensions = [str(i).lower() for i in args.extensions.split(',')]
    args.raw_extensions = [str(i).lower() for i in args.raw_extensions.split(',')]
    return args

args = parse_args()
Structure.make(args.path, args.extensions, args.raw_extensions, args.cores)
