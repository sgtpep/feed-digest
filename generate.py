import os
import sqlite3
import glob
import collections
import datetime
import codecs
import urlparse
import urllib

import config

if __name__ == '__main__':
    connection = sqlite3.connect(config.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
    SELECT (strftime('%s', added) - 1 + :interval) / :interval * :interval AS group_timestamp, *
    FROM entries
    ORDER BY group_timestamp DESC, feed_number, added DESC, number
    """, {'interval': config.GROUP_INTERVAL})
    entries = cursor.fetchall()

    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    html_paths = glob.glob(os.path.join(config.OUTPUT_DIR, "*.html"))
    for html_path in html_paths:
        os.remove(html_path)

    header_html = """\
    <html>
    <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>%s</title>
    <style>
    body {
      font: 14px / 1 sans-serif;
    }
    a {
      color: inherit;
      text-decoration: none;
    }
    a:visited {
      color: dimgrey;
    }
    </style>
    </head>
    <body>
    <h2>%s</h2>
    """
    page_title = "Feeds Digest"

    feed_lines = open(config.URLS_PATH).read().strip().splitlines()
    feed_lines = [l.rstrip().split(None, 1) for l in feed_lines if not l.lstrip().startswith('#')]
    feed_titles = dict(l for l in feed_lines if len(l) > 1)

    groups = []
    prev_entry = collections.defaultdict(lambda: None)
    for entry in entries:
        if entry['group_timestamp'] != prev_entry['group_timestamp']:
            group_datetime = datetime.datetime.utcfromtimestamp(entry['group_timestamp'])
            group_filename = group_datetime.strftime("%Y-%m-%d-%H-%M") + ".html"
            group_path = os.path.join(config.OUTPUT_DIR, group_filename)
            f = codecs.open(group_path, 'w', encoding='utf8')

            group_title = group_datetime.strftime("%a %-d %b %-H:%M")
            print >> f, header_html % ("%s &mdash; %s" % (group_title, page_title), group_title)

            groups.append((group_datetime, group_filename))

        if entry['feed_url'] != prev_entry['feed_url']:
            feed_title = feed_titles.get(entry['feed_url']) or entry['feed_title']
            print >> f, """<h4>%s</h4>""" % feed_title

        if entry['url'].startswith('#error') and entry['feed_url'] == prev_entry['feed_url'] and entry['title'] == prev_entry['title']:
            continue

        url = entry['url']
        parsed_url = urlparse.urlparse(url)
        if parsed_url.query:
            query = urlparse.parse_qs(parsed_url.query)
            filtered_query = dict((k, v) for k, v in query.iteritems() if not k.startswith('utm_') and (k, v[0]) != ('from', 'rss'))
            if query != filtered_query:
                query = urllib.urlencode(filtered_query, doseq=True)
                parsed_url = parsed_url._replace(query=query)
                url = parsed_url.geturl()
        if url.startswith('#error'):
            url = entry['feed_url']
        print >> f, """<p><a href="%s">%s</a></p>""" % (url, entry['title'])

        prev_entry = entry

    index_path = os.path.join(config.OUTPUT_DIR, "index.html")
    f = codecs.open(index_path, 'w', encoding='utf8')

    group_title = group_datetime.strftime("%a %-d %b %-H:%M")
    print >> f, header_html % (page_title, page_title)

    prev_group_datetime = None
    now = datetime.datetime.now()
    for group_datetime, group_filename in groups:
        if not prev_group_datetime or group_datetime.year != prev_group_datetime.year or group_datetime.month != prev_group_datetime.month or group_datetime.day != prev_group_datetime.day:
            prev_group_datetime = group_datetime

            print >> f, """<h4>%s</h4>""" % group_datetime.strftime("%a %-d %b")

        link_text = group_datetime.strftime("%-H:%M")
        if group_datetime > now:
            group_filename += '?' + now.strftime("%s")
            link_text = """<i>%s</i>""" % link_text
        print >> f, """<a href="%s">%s</a>&nbsp;&nbsp;""" % (group_filename, link_text)
