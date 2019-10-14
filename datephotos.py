# Problem:
#
# It is often desirable to show photos taken during a trip in chronological
# order. The problem is that many slideshow program display photos in the
# lexical order by file name. This creates a problem when photos are taken
# with multiple devices, even when such devices to time-synchronized.
#
# Solution:
#
# The solution is to prepend timestamp to the filename so that the
# chronological and lexicographical order become the same.
#
# Implementation:
#
# This utility extracts the time when the photo was taken from the
# EXIF metadata of the photo and renames the file by prepending the
# timestamp in the "YYYYMMDDHHMMSS__" format to the filename.
#
import os
import exifread
import pprint
import argparse
from collections import namedtuple

ExtensionsDefault = 'jpg jpeg tiff gif png'
Extensions = ExtensionsDefault.split()
SeparatorDefault = '__'
Truth = ('y',)


def boolify(arg):
    if arg in Truth:
        return True
    else:
        return False


def parse_command_line_args():

    dryrun = False
    recursive = False

    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add requied the arguments to the parser
    ap.add_argument('-i', '--imagedir',
                    required=True,
                    help='Directory with images')

    # Add optional the arguments to the parser
    ap.add_argument('-d', '--dryrun',
                    required=False,
                    choices=Truth,
                    help='Do a dry run without changing any files')
    ap.add_argument('-e', '--extensions',
                    required=False,
                    default=ExtensionsDefault,
                    help='File extensions to process (a space-separated string)')
    ap.add_argument('-r', '--recursive',
                    required=False,
                    choices=Truth,
                    help='Process directory recursively')
    ap.add_argument('-s', '--separator',
                    required=False,
                    default=SeparatorDefault,
                    help='Specify the separator string between the timestamp and the file name')
    ap.add_argument('-u', '--undo',
                    required=False,
                    choices=Truth,
                    help='Strip the header')

    args = vars(ap.parse_args())

    args['dryrun'] = boolify(args['dryrun'])
    args['extensions'] = args['extensions'].lower().split()
    args['imagedir'] = args['imagedir']
    args['recursive'] = boolify(args['recursive'])
    args['undo'] = boolify(args['undo'])

    return args


def parse_exif_data(path, filename):

    file_path = os.path.join(path, filename)

    # Open image file for reading (binary mode)
    f = open(file_path, 'rb')

    # Return Exif tags
    tags = exifread.process_file(f, details=False)

    try:
        dto = str(tags['EXIF DateTimeOriginal']) # Format: (0x9003) ASCII=2019:09:20 20:28:22 @ 61
        dt, tm = dto.split()
        year, month, day = dt.split(':')
        hour, minute, second = tm.split(':')
        return (year, month, day, hour, minute, second)

    except KeyError:
        return None
        

def log_rename(old_filename, new_filename=None):
    if new_filename:
        print('[YES]: %s -> %s' % (old_filename, new_filename))
    else:
        print('[ NO]: %s' % old_filename)


def rename_file(path, filename, args, year, month, day, hour, minute, second):

    dryrun = args['dryrun']
    extensions = args['extensions']
    separator = args['separator']
    undo = args['undo']

    extension = filename.split('.')[-1]

    if extension.lower() not in extensions:
        log_rename(filename)
        return 0

    if separator in filename:
        prefix = filename.split(separator)[0]
        if len(prefix) == 14 and prefix.isdigit():
            if undo:
                return do_rename(path, filename, filename[14+len(separator):], dryrun)
            else:
                log_rename(filename)
                return 0

    if not undo:
        return do_rename(path, filename,
                         ''.join((year, month, day, hour, minute, second, separator, filename)),
                         dryrun)

    log_rename(filename)
    return 0


def do_rename(path, old_filename, new_filename, dryrun):
    log_rename(old_filename, new_filename)
    if dryrun:
        return 0
    else:
        os.rename(os.path.join(path, old_filename), os.path.join(path, new_filename))
        return 1
    

def main():

    renamed_files = 0
    args = parse_command_line_args()
    recursive = args['recursive']
    root_dir = args['imagedir']
    extensions = args['extensions']

    for dir_name, subdir_list, file_list in os.walk(root_dir):
        for filename in file_list:
            dt = parse_exif_data(dir_name, filename)
            if dt:
                renamed_files += rename_file(dir_name, filename, args, *dt)
        if not recursive:
            break

    print('Renamed %d files' % renamed_files)


if __name__ == '__main__':
    main()
