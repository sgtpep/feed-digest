# Feed Digest
Feed Digest is ultra-minimalist, but efficient feed (RSS, Atom, etc.) reader. It downloads feeds by cron and generates entries digest as HTML pages optimized for speed overviewing.

## Dependencies
- Python 2
- Universal Feed Parser. Available as `feedparser` Python package and `python-feedparser` package on some Linux distos.

## Usage
1. Clone or copy this repository to some place on your server, e.g. `~/feed-digest`.
2. Copy `config.example.py` to `config.py`, adjust its values if needed.
3. Copy `urls.example` to `urls`, fill it with your feed urls, start comments with `#`, optionally provide custom feed title after url separating with space.
4. Open crontab using `crontab -e` and edit cronjob to it like `*/20 * * * * cd ~/feed-digest; python2 ./download.py; python2 ./generate.py`
5. Symlink directory with generated HTML files to webserver root: `sudo ln -s ~/feed-digest/www/ /var/www/feeds`
6. Your Feed Digest will be available for reading by http://yourserver/feeds/.

## Similar Projects
- [rawdog](http://offog.org/code/rawdog/)
