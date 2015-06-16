import os
import sqlite3
import glob
import collections
import datetime
import codecs
import cgi
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
    WHERE added >= date('now', :period)
    ORDER BY group_timestamp DESC, feed_number, added DESC, number
    """, {'interval': config.GROUP_INTERVAL, 'period': '-' + config.GENERATE_PERIOD})
    entries = cursor.fetchall()

    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    html_paths = glob.glob(os.path.join(config.OUTPUT_DIR, "*.html"))
    for html_path in html_paths:
        os.remove(html_path)

    header_html = u"""\
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{0}</title>
    <style>
    body {{
      margin: 25px;
      font-family: sans-serif;
      line-height: 1.6;
    }}
    h1 {{
      font-size: 1.5em;
      line-height: 1em;
    }}
    h2 {{
      font-size: 1em;
      margin: 0.3em 0;
    }}
    a {{
      color: inherit;
      text-decoration: none;
    }}
    a:visited {{
      color: dimgrey;
    }}
    a.is-active {{
      color: inherit;
      font-weight: bold;
    }}
    {2}
    </style>
    </head>
    <body>
    <h1>{1}</h1>
    """
    page_title = u"Feeds Digest"

    feed_lines = open(config.URLS_PATH).read().strip().splitlines()
    feed_lines = [l.rstrip().split(None, 1) for l in feed_lines if not l.lstrip().startswith('#')]
    feed_titles = dict(l for l in feed_lines if len(l) > 1)

    def escape(string):
        return string.replace('<', "&lt;").replace('>', "&gt;")

    groups = []
    prev_entry = collections.defaultdict(lambda: None)
    prev_group_datetime = None
    for entry in entries:
        if entry['group_timestamp'] != prev_entry['group_timestamp']:
            group_datetime = datetime.datetime.utcfromtimestamp(entry['group_timestamp'])
            group_filename = group_datetime.strftime("%Y-%m-%d-%H-%M") + ".html"
            group_path = os.path.join(config.OUTPUT_DIR, group_filename)
            f = codecs.open(group_path, 'w', encoding='utf8')
            group_header = group_datetime.strftime("%a %-d %b %-H:%M")
            group_title = u"{} &ndash; {}".format(group_header, page_title)
            print >> f, header_html.format(group_title, group_header, '')

            print >> f, u"""
            <script>
            (function() {
            var lastFilename = location.pathname.replace(/^.*\//, '');
            document.cookie = "feed-digest-last-filename=" + lastFilename + "; expires=Fri, 31 Dec 9999 23:59:59 GMT";
            })();
            </script>
            """
            print >> f, u"""<!--#exec cmd="echo \\"<script>var lastFilename = \\\\"{}\\\\";</script>\\" > /var/tmp/feed-digest-last-filename.html" -->""".format(group_filename)

            if not prev_group_datetime or group_datetime.year != prev_group_datetime.year or group_datetime.month != prev_group_datetime.month or group_datetime.day != prev_group_datetime.day:
                prev_group_datetime = group_datetime
                groups.append([])
            groups[len(groups) - 1].append((group_datetime, group_filename))

            prev_entry = collections.defaultdict(lambda: None)

        if entry['feed_url'] != prev_entry['feed_url']:
            feed_title = feed_titles.get(entry['feed_url']) or entry['feed_title']
            print >> f, u"""<h2>{}</h2>""".format(escape(feed_title))

        url = entry['url']
        parsed_url = urlparse.urlparse(url)
        if parsed_url.query:
            query = urlparse.parse_qs(parsed_url.query)
            filtered_query = dict((k, v) for k, v in query.iteritems() if not k.startswith('utm_'))
            if query != filtered_query:
                query = urllib.urlencode(filtered_query, doseq=True)
                parsed_url = parsed_url._replace(query=query)
                url = parsed_url.geturl()
        print >> f, u"""<div><a href="{}">{}</a></div>""".format(url, escape(entry['title']))

        prev_entry = entry

    index_path = os.path.join(config.OUTPUT_DIR, "index.html")
    f = codecs.open(index_path, 'w', encoding='utf8')
    page_style = u"""
    a {
      margin-right: 0.5em;
    }
    """
    print >> f, header_html.format(page_title, page_title, page_style)

    now = datetime.datetime.now()
    for subgroups in groups:
        group_datetime = subgroups[0][0]
        print >> f, u"""<h2>{}</h2>""".format(group_datetime.strftime("%a %-d %b"))

        for group_datetime, group_filename in reversed(subgroups):
            link_text = group_datetime.strftime("%-H:%M")
            if group_datetime > now:
                group_filename += '?' + now.strftime("%s")
                link_text = u"""<i>{}</i>""".format(link_text)
            print >> f, u"""<a href="{}">{}</a>""".format(group_filename, link_text)

    print >> f, u"""
    <!--#exec cmd="cat /var/tmp/feed-digest-last-filename.html" --> 

    <script>
    (function() {
    if (!window.lastFilename) {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].replace(/^\s*(.+)\s*$/, '$1').split('=');
        if (cookie[0] != 'feed-digest-last-filename') continue;

        window.lastFilename = cookie[1];
        break;
      }
    }

    function onLinkClick(event) {
      var activeLinks = document.getElementsByClassName('is-active');
      if (activeLinks.length) activeLinks[0].removeAttribute('class');

      var link = event.target;
      link.className = 'is-active';
    }

    var links = document.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {
      var link = links[i];
      link.onclick = onLinkClick;

      var href = link.getAttribute('href');
      if (href == lastFilename) link.className = 'is-active';
    }
    })();
    </script>
    """

    stats_path = os.path.join(config.OUTPUT_DIR, "stats.html")
    f = codecs.open(stats_path, 'w', encoding='utf8')
    stats_header = u"Stats"
    stats_title = u"{} &mdash; {}".format(stats_header, page_title)
    print >> f, header_html.format(stats_title, stats_header, '')

    cursor.execute("""
    SELECT max(published), count(*), feed_url, feed_title
    FROM entries
    GROUP BY feed_url
    ORDER BY published
    """)
    feeds = cursor.fetchall()

    print >> f, u"""
    <table cellspacing="5">
    <tr>
    <th>Last Published</th>
    <th align="right">Count</th>
    <th align="left">Feed</th>
    </tr>
    """
    for last_published, count, feed_url, feed_title in feeds:
        feed_title = feed_titles.get(feed_url) or feed_title

        print >> f, u"<tr>"
        print >> f, u"""<td>{}</td>""".format(last_published)
        print >> f, u"""<td align="right">{:d}</td>""".format(count)
        print >> f, u"""<td><a href="{}">{}</a></td>""".format(feed_url, escape(feed_title))
        print >> f, u"</tr>"
    print >> f, u"</table>"
