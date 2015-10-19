# Feed Digest
Feed Digest is an ultra-minimalist, but efficient feed reader of RSS and Atom feeds. It consists of two commands for feeds downloading and generating of HTML digest optimized for fast titles overviewing.

## Dependencies
- Python 2+
- Universal Feed Parser. Available as `feedparser` Python package and `python-feedparser` package on some Linux distos.

## Screenshots

_Index page:_

![screenshot 1](https://github.com/sgtpep/feed-digest/raw/master/screenshots/1.png)

_Hourly entries:_

![screenshot 1](https://github.com/sgtpep/feed-digest/raw/master/screenshots/2.png)

## Usage
1. Clone or copy this repository to some place on your server, e.g. `~/feed-digest`.
2. Copy `config.example.py` to `config.py`, adjust its values if needed.
3. Copy `urls.example` to `urls`, fill it with your feed urls, start comments with `#`, optionally provide custom feed title after url separating with space.
4. Open crontab using `crontab -e` and edit cronjob to it like `*/20 * * * * cd ~/feed-digest; ./download && ./generate`
5. Symlink directory with generated HTML files to webserver root: `sudo ln -s ~/feed-digest/www/ /var/www/feeds`
6. Your Feed Digest will be available for reading by http://yourserver/feeds/.

## Similar projects
- [rawdog](http://offog.org/code/rawdog/)
- [Litenin](http://liten.in/)

## License and copyright

The project is released under the General Public License (GPL), version 3.

Copyright © 2015, Danil Semelenov.
