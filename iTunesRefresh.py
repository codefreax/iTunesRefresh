#!/usr/bin/env python
import datetime
import os
import sys
import appscript
import mactypes

verbose = False

new_playlist_name = 'Import %s' % datetime.datetime.now().strftime('%Y/%m/%d %H:%M')

def get_track_data(track):
    track_data = {
            'artist'   : track.artist(),
            'album'    : track.album(),
            'name'     : track.name(),
            'video'    : track.video_kind(),
            'kind'     : track.kind(),
            'time'     : track.time(),
            'location' : track.location(),
            }
    return track_data

def bundle_path(path):
    return path.endswith('.itlp') # iTunes LPs

def ignored_path(path):
    return (   path.startswith(itunes_lib_path + '/' + 'Podcasts')
            or path.startswith(itunes_lib_path + '/' + 'Tones')
            or path.startswith(itunes_lib_path + '/' + 'Automatically Add to iTunes.localized'))

def ignored_file(file):
    return file.startswith('.')

itunes_lib_path = os.environ['HOME'] + u'/Music/iTunes/iTunes Music'

print 'Searching for music in %s' % repr(itunes_lib_path)

files_on_disk = []
for walk_path, walk_dirs, walk_files in os.walk(itunes_lib_path, topdown=True):
    if not ignored_path(walk_path):
        files_on_disk.extend([walk_path + os.sep + file for file in walk_files if not ignored_file(file)])

        for idx, walk_dir in reversed(list(enumerate(walk_dirs))):
            if bundle_path(walk_dir):
                # Do not walk bundles but treat them as a single object
                del walk_dirs[idx]
                files_on_disk.append(walk_path + os.sep + walk_dir)

print '%s files found' % len(files_on_disk)
if 0:
    print '\t' + '\n\t'.join([repr(x) for x in files_on_disk])

print 'Connecting to iTunes'
itunes = appscript.app('itunes')

library = itunes.library_playlists()[0]
library_tracks = library.file_tracks()
print 'Playlist "%s" contains %s files of %s MB. This is %s of music.' % (
        library.name(), len(library_tracks), library.size() / 1024 / 1024, library.time()
        )

print

print 'Checking iTunes track list'

tracks_to_remove = []
files_to_add = list(files_on_disk)

idx_format = '%%%ss/%s' % (len(str(len(library_tracks))), len(library_tracks))

for idx, track in enumerate(library_tracks):
    if track.podcast():
        if verbose:
            print idx_format % (idx + 1) + ' Skipping podcast %s' % ', '.join(['%s=%s' % (k, repr(v)) for k, v in get_track_data(track).iteritems()])
        continue

    if track.location() == appscript.k.missing_value:
        message = 'item with unknown location %s' % ', '.join(['%s=%s' % (k, repr(v)) for k, v in get_track_data(track).iteritems()])
        print idx_format % (idx + 1) + ' ' + message
        tracks_to_remove.append((track, message))
        continue

    path = track.location().path
    if path in files_to_add:
        if verbose:
            print idx_format % (idx + 1) + ' Found    %s' % repr(path)
        files_to_add.remove(path)
    else:
        message = 'track with missing file %s' % repr(path)
        print idx_format % (idx + 1) + ' ' + message
        tracks_to_remove.append((track, message))

# Get list of playlists
user_playlists = dict([(list.name(), list) for list in itunes.user_playlists()])
try:
    new_playlist = user_playlists[new_playlist_name]
except KeyError:
    new_playlist = None

print

# Print task list for approval
print '%s tracks to remove' % len(tracks_to_remove)
idx_format = '%%%ss/%s' % (len(str(len(tracks_to_remove))), str(len(tracks_to_remove)))
for idx, (track, message) in enumerate(tracks_to_remove):
    print idx_format % (idx + 1) + ' Remove ' + message

print '%s new files to add' % len(files_to_add)
idx_format = '%%%ss/%s' % (len(str(len(files_to_add))), str(len(files_to_add)))
for idx, path in enumerate(files_to_add):
    print idx_format % (idx + 1) + ' Add %s' % repr(path)

if len(tracks_to_remove) or len(files_to_add):
    # Ask for permission
    print 'Press Enter to continue or Ctrl-C to quit.'
    sys.stdin.readline()

    # Run tasks
    print 'Removing %s tracks' % len(tracks_to_remove)
    idx_format = '%%%ss/%s' % (len(str(len(tracks_to_remove))), str(len(tracks_to_remove)))
    for idx, (track, message) in enumerate(tracks_to_remove):
        print idx_format % (idx + 1) + ' Removing ' + message
        library.delete(track)

    print 'Adding %s new files' % len(files_to_add)
    idx_format = '%%%ss/%s' % (len(str(len(files_to_add))), str(len(files_to_add)))
    for idx, path in enumerate(files_to_add):
        if not new_playlist:
            print 'Creating playlist %s' % repr(new_playlist_name)
            new_playlist = itunes.make(new=appscript.k.user_playlist, with_properties={appscript.k.name: new_playlist_name})

        print idx_format % (idx + 1) + ' Adding %s' % repr(path)
        library.add(mactypes.File(path).hfspath, to=new_playlist)

