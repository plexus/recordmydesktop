Fork of the seemingly unmaintained RecordMyDesktop application.

If you need Jack support you will need this version, the last release (from 2010) is no longer compatible with the latest versions of Jack.

This fork contains this patch: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=588260

Plus one other commit to fix Jack support.

If you see this when using `--use-jack` (e.g. `recordmydesktop --use-jack system:capture_1 -o output.ogv`)

```
jack_client_new: deprecated
```

Then your version is affected.

To build on Ubuntu 15.10 (possibly also works on Debian)

```
sudo apt-get build-dep recordmydesktop
sudo apt-get install libpopt-dev libvorbis-dev libtheora-dev libjack-dev
./autogen.sh && ./configure && make
```

Based on the SVN trunk@602

Project website: http://recordmydesktop.sourceforge.net/about.php

SVN->Git import by [@jamoozy](https://github.com/jamoozy)
Jack fixes by [@plexus](https://github.com/plexus)
