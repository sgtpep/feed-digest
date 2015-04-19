import os
import datetime
import socket
import sqlite3
import feedparser
from multiprocessing import Pool

import config

def parse_feed(feed_url):
    result = feedparser.parse(feed_url, agent="Mozilla/5.0 (X11; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0")
    if not result.feed.has_key('title'):
        result.feed['title'] = feed_titles.get(feed_url)
    if not result.entries:
        result.entries = [{
            'title': repr(result.bozo_exception),
            'link': '#error%s' % added.strftime('%s'),
        }]

    return feed_url, result.feed, result.entries

if __name__ == '__main__':
    added = datetime.datetime.now()
    added -= datetime.timedelta(0, added.second, added.microsecond)
    if not os.path.exists(config.DB_PATH):
        added -= datetime.timedelta(seconds=config.GROUP_INTERVAL)

    connection = sqlite3.connect(config.DB_PATH)
    cursor = connection.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS entries (
        feed_number INTEGER, feed_url TEXT, feed_title TEXT, number INTEGER, url TEXT, title TEXT, added TIMESTAMP,
        PRIMARY KEY (feed_url, url)
    );
    CREATE INDEX IF NOT EXISTS entries_order ON entries (feed_number, added, number);
    """)

    feed_lines = open(config.URLS_PATH).read().strip().splitlines()
    feed_urls = [l.split(None, 1)[0] for l in feed_lines if not l.lstrip().startswith('#')]

    cursor.execute("SELECT feed_url, feed_title FROM entries GROUP BY feed_url")
    feed_titles = dict(cursor.fetchall())

    socket.setdefaulttimeout(config.SOCKET_TIMEOUT)

    pool = Pool(config.NUMBER_OF_PROCESSES)
    results = pool.map(parse_feed, feed_urls)
    pool.close()
    pool.join()
    
    rows = []
    for feed_number, (feed_url, feed, entries) in enumerate(results):
        feed_title = feed.get('title') or feed_url
        for number, entry in enumerate(entries):
            url = entry.get('link', '')
            title = entry.get('title') or url

            result = cursor.execute("UPDATE entries SET title = ? WHERE feed_url = ? AND url = ?", (title, feed_url, url))
            if not result.rowcount:
                rows.append((feed_number, feed_url, feed_title, number, url, title, added))
    cursor.executemany("INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    connection.commit()
