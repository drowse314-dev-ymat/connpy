# encoding: utf-8

import unittest
import datetime
import connpy


class TestSearchEvent(unittest.TestCase):
    """Tests for searching connpass events functionality."""

    def test_api_get_success(self):
        """Assert GET-API-URI request successes."""
        pysearch = {'keyword': 'Python'}  # Suppose there exists at least A Python event!
        res = connpy.api_get(pysearch)
        self.assertEqual(res.status_code, 200)

    def test_search_events(self):
        """Assert connpass event searching works."""
        res = connpy.kw_search()  # Apply keyword='Python' as default...
        self.assertTrue(isinstance(res, dict))
        res = connpy.kw_search(search_or=True)  # Just check 'or' works.
        self.assertTrue(isinstance(res, dict))

    def test_multiple_kw(self):
        """Assert kw_search allows multiple keywords."""
        keywords = ['Python', 'Flask']
        res = connpy.kw_search(keywords)
        self.assertTrue(isinstance(res, dict))
        keywords = (kw for kw in ['Python', 'Flask'])
        res = connpy.kw_search(keywords)
        self.assertTrue(isinstance(res, dict))

    def test_search_configs(self):
        """Assert several search configuration works."""
        # Count ristriction.
        res = connpy.kw_search(count=3)
        self.assertEqual(res['results_returned'], 3)
        # Date setting.
        res = connpy.kw_search(event_date=20130101)
        self.assertTrue(isinstance(res, dict))
        res = connpy.kw_search(event_date=201301)
        self.assertTrue(isinstance(res, dict))
        with self.assertRaises(ValueError):
            res = connpy.kw_search(event_date=2010301)

    def test_search_offset(self):
        """Assert search offset works."""
        # Head 2 events.
        res = connpy.kw_search(count=2)
        # Check with offset 1.
        res_offset1 = connpy.kw_search(count=1, offset=2)
        self.assertEqual(
            res['events'][1],
            res_offset1['events'][0],
        )


class TestFormatter(unittest.TestCase):
    """Format printer tests."""

    def setUp(self):
        # Prepare only i want...
        self.result = {
            'results_returned': 2,
            'events': [
                {
                    'event_id': 365,
                    'title': u'Pyhack',
                    'catch': u'Pyhackするよ',
                    'description': u'Pyhackするよ---',
                    'event_url': u'http://connpass.com/about/api/',
                    'owner_nickname': u'ymat',
                    'hash_tag': u'pyhack',
                    'started_at': u'2012-04-17T18:30:00+09:00',
                    'ended_at': u'2012-04-17T20:30:00+09:00',
                    'limit': 30,
                    'accepted': 30,
                    'waiting': 15,
                    'address': u'東京都渋谷区代々木1-2-9',
                    'place': u'BPオフィス (森京ビル2F)',
                },
                {
                    'event_id': 369,
                    'title': u'Pyhack2',
                    'catch': u'Pyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよー',
                    'description': u'Pyhack2するよ---',
                    'event_url': u'http://connpass.com/about/api/',
                    'owner_nickname': u'ymat',
                    'hash_tag': u'pyhack',
                    'started_at': u'2012-05-17T18:30:00+09:00',
                    'ended_at': u'2012-05-17T20:30:00+09:00',
                    'limit': 30,
                    'accepted': 30,
                    'waiting': 15,
                    'address': u'東京都渋谷区代々木1-2-9',
                    'place': u'BPオフィス (森京ビル2F)',
                },
            ]
        }

    def test_style(self):
        """Check printing formats."""
        self.assertEqual(
            '\n'.join(connpy.format_event(self.result['events'][0])),
u"""\
-----------------------------------------
Date: 2012/04/17 18:30 - 2012/04/17 20:30
#365 'Pyhack'  by ymat
-----------------------------------------
* Place: BPオフィス (森京ビル2F)
         東京都渋谷区代々木1-2-9
* Participants: 30/30 (15 waiting)
* Tags: #pyhack

Pyhackするよ
\
"""
        )
        self.assertEqual(
            '\n'.join(connpy.format_event(self.result['events'][1])),
u"""\
-----------------------------------------
Date: 2012/05/17 18:30 - 2012/05/17 20:30
#369 'Pyhack2'  by ymat
-----------------------------------------
* Place: BPオフィス (森京ビル2F)
         東京都渋谷区代々木1-2-9
* Participants: 30/30 (15 waiting)
* Tags: #pyhack

Pyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよーPyhack2するよー
\
"""
        )  # No wrap though long...

    def test_isoformat(self):
        """Test iso-8601 format conversion."""
        isoformat = '2012-05-17T18:30:00+09:00'
        self.assertEqual(
            connpy._iso2datetime(isoformat),
            datetime.datetime(2012, 5, 17, 18, 30)
        )
        t = datetime.datetime(2012, 5, 17, 18, 30)
        self.assertEqual(
            connpy._datetime2readable(t),
            '2012/05/17 18:30'
        )
