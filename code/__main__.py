from joblib import cpu_count
from structure import Structure
from pycloud import Transfer
import argparse
import os

def parse_args():
    # get args
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', help='Pcloud Username', type=str, required=True)
    parser.add_argument('--password', help='Pcloud Password', type=str, required=True)
    parser.add_argument('--pcloudpath', help='Path of Pcloud Pictures Pictures', type=str, required=True)
    parser.add_argument('--path', help='Path of Pictures', type=str, required=True)
    parser.add_argument('--extensions', help='Extensions of pictures', type=str, required=True)
    parser.add_argument('--raw-extensions', help='Extensions of raw pictures', type=str, required=True)
    parser.add_argument('--cores', help='Number of cores', type=int, default=int(cpu_count()), required=False)
    args = parser.parse_args()
    # clean args
    args.path = os.path.realpath(os.path.expanduser(args.path))
    args.pcloudpath = '/' + os.path.join(*filter(bool, args.pcloudpath.split('/')))
    args.extensions = [str(i).lower() for i in args.extensions.split(',')]
    args.raw_extensions = [str(i).lower() for i in args.raw_extensions.split(',')]
    return args

args = parse_args()
#Structure.make(args.path, args.extensions, args.raw_extensions, args.cores)
t = Transfer(username=args.username, password=args.password)
ls = t.check_folders(pcloudpath=args.pcloudpath, path=args.path, extensions=args.extensions + args.raw_extensions)
print(ls)