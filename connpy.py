# encoding: utf-8
"""
    connpy
    ~~~~~~

    Search connpass events on CLI!

    :copyright: (c) 2013 by drowse314-dev-ymat@github.com.
    :licence: BSD
"""

import sys
import argparse
import collections
import datetime
import requests


__version__ = '0.1.0'
__api_version__ = 'v1'


API_URI = 'http://connpass.com/api/{}/event/'.format(__api_version__)


def api_get(params):
    """GET API URI resource."""
    return requests.get(API_URI, params=params)

def kw_search(keyword='Python', search_or=False,
              count=None, event_date=None, offset=1):
    """Search connpass events."""
    # AND or OR...
    if search_or:
        kwname = 'keyword_or'
    else:
        kwname = 'keyword'
    # Multiple keywords.
    if isinstance(keyword, collections.Iterable):
        keyword = ','.join(keyword)
    # Make parameters.
    params = {}
    params[kwname] = keyword
    # Options.
    if isinstance(count, int) and count > 0:
        params['count'] = count
    if isinstance(event_date, int):
        if len(str(event_date)) == 6:
            datetype = 'ym'
        elif len(str(event_date)) == 8:
            datetype = 'ymd'
        else:
            raise ValueError('not a format for ymd or ym: {}'.format(event_date))
        params[datetype] = event_date
    params['start'] = offset
    return api_get(params).json()

def pagerized_search(**kwargs):
    """
    Pagerize `kw_search` calls.
    
    Generates generators of <count> events.
    """
    if 'count' not in kwargs:
        raise KeyError('argument `count` is needed!')
    step = kwargs['count']
    # Force to start from top...
    kwargs['offset'] = 1
    while True:
        res = kw_search(**kwargs)
        events = res['events']
        if len(events) == 0:
            break
        else:
            yield (event for event in events)
        kwargs['offset'] += step

def _iso2datetime(iso_char):
    return datetime.datetime.strptime(iso_char[:16], '%Y-%m-%dT%H:%M')

def _datetime2readable(dtobj):
    return datetime.datetime.strftime(dtobj, '%Y/%m/%d %H:%M')

def format_event(event):
    """
    Pretty print search result.

    Genarates result lines.
    """
    # Make date line.
    from_date = _iso2datetime(event['started_at'])
    to_date = _iso2datetime(event['ended_at'])
    date_line = u'Date: {} - {}'.format(
        _datetime2readable(from_date),
        _datetime2readable(to_date)
    )
    line_length = len(date_line)
    yield '-' * line_length
    yield date_line
    # Event abst.
    yield u"#{evt_no} '{title}'  by {planner}".format(
        evt_no=event['event_id'],
        title=event['title'],
        catch=event['catch'],
        planner=event['owner_nickname'],
    )
    yield '-' * line_length
    # Place.
    yield u'* Place: {}'.format(event['place'])
    yield u'         {}'.format(event['address'])
    # Participants.
    yield u'* Participants: {}/{} ({} waiting)'.format(
        event['accepted'], event['limit'], event['waiting'],
    )
    # Tags.
    yield u'* Tags: #{}'.format(event['hash_tag'])
    # Description.
    yield u''
    for line in event['catch'].split('\n'):
        yield line
    yield u''

def events_printer(events):
    """Print events & returns items count."""
    printed = 0
    for event in events:
        printed += 1
        for line in format_event(event):
            print(line)
    return printed

def cli_pager(**options):
    """Manage pagerizing event prints on CLI."""
    msg = '--next page? [y/n]--'
    evt_pages_gen = pagerized_search(**options)
    for events_generator in evt_pages_gen:
        item_shown = events_printer(events_generator)
        if item_shown < options['count']:
            break
        while True:
            try:
                next_code = raw_input(msg)
            except NameError:
                next_code = input(msg)
            if next_code in ('y', 'n'):
                break
        if next_code.startswith('n'):
            break
    evt_pages_gen.close()

def _search(pagerize, **options):
    if pagerize:
        cli_pager(**options)
    else:
        res = kw_search(**options)
        events = res['events']
        events_printer(events)

def search():
    """Search command handler."""
    parser = argparse.ArgumentParser(
        description='connpass event search API CLI v{}'.format(__version__)
    )
    parser.add_argument('search')  # ignore this!
    parser.add_argument('keywords', type=unicode, nargs='+',
                        help='keywords to search')
    parser.add_argument('--search_or', action='store_true', default=False,
                        help='set or-search on')
    parser.add_argument('-n', '--nitem', type=int, default=3, help='items per page')
    parser.add_argument('-d', '--date', type=int,
                        help="date formed 'yyyymm' or 'yyyymmdd'")
    parser.add_argument('-p', '--pagerize_not', action='store_true', default=False,
                        help='do not pagerize output')
    args = parser.parse_args()
    # Collect options.
    kwargs = {}
    kwargs['keyword'] = args.keywords
    kwargs['search_or'] = args.search_or
    kwargs['count'] = args.nitem
    kwargs['event_date'] = args.date
    # Search...
    _search(not args.pagerize_not, **kwargs)

def browse():
    """Browse command handler."""
    parser = argparse.ArgumentParser(
        description='connpass event browser CLI v{}'.format(__version__)
    )
    parser.add_argument('browse')  # ignore this!
    parser.add_argument('event_id', type=int, help='connpass event id')
    args = parser.parse_args()
    import webbrowser
    platform_maps = {
        'win32': 'windows-default',
        'cygwin': 'windows-default',
        'darwin': 'macosx',
    }
    browser_name = platform_maps.get(sys.platform, None)
    webbrowser.get(browser_name).open('http://connpass.com/event/{}/'.format(args.event_id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='connpass API CLI handler v{}'.format(__version__)
    )
    # Action routings.
    actions = [
        'search',
        'browse',
    ]
    action_funcs = {
        'search': search,
        'browse': browse,
    }
    parser.add_argument('action',
                        help='ACTION: ( {} )'.format(', '.join(actions)),
                        choices=actions)
    # Parse & execute.
    args = parser.parse_args(sys.argv[1:2])
    action_funcs[args.action]()
