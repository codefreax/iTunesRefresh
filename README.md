iTunesRefresh
=============

iTunesRefresh will scan your "~/Music/iTunes/iTunes Music" folder and inform iTunes about new and deleted files. This is specifically useful after synchronizing music with another computer.

iTunesRefresh is a Python command line script and requires the appscript module. Install the module with the following command:
<pre>
easy_install appscript
</pre>

Then just start the script:
<pre>
# ./iTunesRefresh.py
Searching for music in /Users/yaron/Music/iTunes/iTunes Music
1385 files found
Connecting to iTunes
Playlist "Library" contains 1432 files of 14420 MB. This is 5:16:34:14 of music.

Checking iTunes track list
[****************************************] (100.0 %)
0 tracks to remove
10 new files to add
 1/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/01 One Step Inside Doesn't Mean You Understand.mp3
 2/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/02 Pilot.mp3
 3/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/03 Pick Up the Phone.mp3
 4/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/04 Trashing Days.mp3
 5/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/05 This Room.mp3
 6/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/06 Solitaire.mp3
 7/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/07 One With the Freaks.mp3
 8/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/08 Neon Golden.mp3
 9/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/09 Off the Rails.mp3
10/10 Add /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/10 Consequence.mp3
Press Enter to continue or Ctrl-C to quit.

Removing 0 tracks
Adding 10 new files
Creating playlist 'Import 2013/05/04 18:43'
 1/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/01 One Step Inside Doesn't Mean You Understand.mp3
 2/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/02 Pilot.mp3
 3/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/03 Pick Up the Phone.mp3
 4/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/04 Trashing Days.mp3
 5/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/05 This Room.mp3
 6/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/06 Solitaire.mp3
 7/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/07 One With the Freaks.mp3
 8/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/08 Neon Golden.mp3
 9/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/09 Off the Rails.mp3
10/10 Adding /Users/yaron/Music/iTunes/iTunes Music/The Notwist/Neon Golden/10 Consequence.mp3
</pre>