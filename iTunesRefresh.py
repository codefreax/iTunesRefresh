#!/usr/bin/env python
from __future__ import print_function

import appscript
import argparse
import datetime
import mactypes
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Refresh iTunes database after library changes on disk.")
    parser.add_argument("-l", "--library", default=None,
                        help="path to iTunes library (default: guess)")
    parser.add_argument("-n", "--dryrun", action="store_true",
                        help="do not apply any changes")
    parser.add_argument("-v", dest="verbosity", action="count", default=0,
                        help="increase verbosity")
    args = parser.parse_args()
    return args


def walk_library(lib_path):
    def is_bundle_path(path):
        res = path.endswith(".itlp")  # iTunes LPs
        res |= path.endswith(".ite")  # iTunes extras
        return res

    def is_ignored_dir(path):
        ignored_dirs = (
            os.path.join(lib_path, "Mobile Applications"),
            os.path.join(lib_path, "Podcasts"),
            os.path.join(lib_path, "Tones"),
            os.path.join(lib_path, "Automatically Add to iTunes.localized"),
            os.path.join(lib_path, "Automatically Add to iTunes.localized", ".localized"),
        )
        res = path in ignored_dirs
        return res

    def is_ignored_file(fn):
        return fn.startswith(".")

    files_found = []
    for walk_path, walk_dirs, walk_files in os.walk(lib_path, topdown=True):
        if is_ignored_dir(walk_path):
            continue

        files_found.extend([walk_path + os.sep + fn for fn in walk_files if not is_ignored_file(fn)])

        for idx, walk_dir in reversed(list(enumerate(walk_dirs))):
            if is_bundle_path(walk_dir):
                # Do not walk bundles but treat them as a single object
                del walk_dirs[idx]
                files_found.append(walk_path + os.sep + walk_dir)

    return files_found


def get_track_data(track):
    track_data = {
        'artist': track.artist(),
        'album': track.album(),
        'name': track.name(),
        'video': track.video_kind(),
        'kind': track.kind(),
        'time': track.time(),
        'location': track.location(),
    }
    return track_data


def main():
    args = parse_args()

    itunes_lib_path = args.library

    print("Connecting to iTunes")
    itunes = appscript.app('itunes')

    library = itunes.library_playlists()[0]
    library_tracks = library.file_tracks()
    print("Playlist \"%s\" contains %s files of %s MB. This is %s of music." % (
          library.name(), len(library_tracks), library.size() / 1024 / 1024, library.time()
          ))

    #print("Searching for iTunes library")
    #if len(library_tracks):
    #    file_paths = [t.location().path for t in library_tracks]
    #    prefix = file_paths[0]
    #    while True:
    #        prefix = os.path.dirname(prefix)
    #        if prefix == "/":
    #            break
    #        count_with_prefix = reduce(lambda c, t: c + (1 if t.startswith(prefix) else 0), file_paths, 0)
    #        if count_with_prefix == len(file_paths):
    #            # Found common prefix
    #            itunes_lib_path = prefix
    #            break

    if not itunes_lib_path:
        # Guess library path
        candidates = (
            os.environ['HOME'] + u"/Music/iTunes/iTunes Media",
            os.environ['HOME'] + u"/Music/iTunes/iTunes Music",
        )
        for path in candidates:
            if os.path.exists(path):
                itunes_lib_path = path
                break

    if not itunes_lib_path:
        print("iTunes library not found")
        return 3

    print("Searching for music in %s" % itunes_lib_path)
    files_on_disk = walk_library(itunes_lib_path)

    print("%s files found" % len(files_on_disk))

    print()

    print("Checking iTunes track list")

    tracks_to_remove = []
    files_to_add = list(files_on_disk)

    tracklist_size = len(library_tracks)
    idx_format = "%%%ss/%s" % (len(str(tracklist_size)), tracklist_size)

    for idx, track in enumerate(library_tracks):
        if not args.verbosity:
            progress_len = 70
            progress = progress_len * (idx + 1) / tracklist_size
            sys.stdout.write("\r[" + progress_len * " " + ("] %5.1f %%" % (100. * (idx + 1) / tracklist_size)))
            sys.stdout.write("\r[" + progress * "*")
            sys.stdout.flush()

        if track.location() == appscript.k.missing_value:
            message = "item with unknown location %s" % ", ".join(["%s=%s" % (k, repr(v)) for k, v in get_track_data(track).iteritems()])
            if args.verbosity >= 1:
                print(idx_format % (idx + 1) + " " + message)
            tracks_to_remove.append((track, message))
            continue

        path = track.location().path
        if path in files_to_add:
            if args.verbosity >= 3:
                print(idx_format % (idx + 1) + " Found %s" % path)
            files_to_add.remove(path)
        else:
            message = "track with missing file %s" % path
            if args.verbosity >= 1:
                print(idx_format % (idx + 1) + " " + message)
            tracks_to_remove.append((track, message))

    # Get list of playlists
    user_playlists = dict([(plist.name(), plist) for plist in itunes.user_playlists()])
    new_playlist_name = "Import %s" % datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    try:
        new_playlist = user_playlists[new_playlist_name]
    except KeyError:
        new_playlist = None

    print()

    # Print task list for approval
    print("%s tracks to remove" % len(tracks_to_remove))
    idx_format = "%%%ss/%s" % (len(str(len(tracks_to_remove))), str(len(tracks_to_remove)))
    for idx, (track, message) in enumerate(tracks_to_remove):
        print(idx_format % (idx + 1) + " Remove " + message)

    print("%s new files to add" % len(files_to_add))
    idx_format = "%%%ss/%s" % (len(str(len(files_to_add))), str(len(files_to_add)))
    for idx, path in enumerate(files_to_add):
        print(idx_format % (idx + 1) + " Add %s" % path)

    if args.dryrun:
        return 0

    if not len(tracks_to_remove) and not len(files_to_add):
        return 0

    # Ask for permission
    print("Press Enter to continue or Ctrl-C to quit.")
    sys.stdin.readline()

    # Run tasks
    print("Removing %s tracks" % len(tracks_to_remove))
    idx_format = "%%%ss/%s" % (len(str(len(tracks_to_remove))), str(len(tracks_to_remove)))
    for idx, (track, message) in enumerate(tracks_to_remove):
        print(idx_format % (idx + 1) + " Removing " + message)
        library.delete(track)

    print("Adding %s new files" % len(files_to_add))
    idx_format = "%%%ss/%s" % (len(str(len(files_to_add))), str(len(files_to_add)))
    for idx, path in enumerate(files_to_add):
        if not new_playlist:
            print("Creating playlist %s" % new_playlist_name)
            new_playlist = itunes.make(new=appscript.k.user_playlist, with_properties={appscript.k.name: new_playlist_name})

        print(idx_format % (idx + 1) + " Adding %s" % path)
        library.add(mactypes.File(path).hfspath, to=new_playlist)

    return 0


if __name__ == '__main__':
    err = main()
    sys.exit(err)
