import urllib.parse
import requests

from .resource import Bill, EDM, Division, parse_data


class Parliament(object):
    def __init__(self):
        self.http = requests.Session()
        self.commons = Commons(self)
        self.lords = House("Lords", self)

    def get_bills(self, limit=50, page=0):
        res = self.get('bills.json', limit, page)
        for item in res['items']:
            b = Bill(self)
            b.resource = item['_about']
            b.title = item['title']
            b.home_page = item['homePage']
            b.type = item['billType']
            b.date = parse_data(item['date']).date()
            yield b

    def get(self, path, limit=None, page=None, **kwargs):
        params = {}
        if limit is not None:
            params['_pageSize'] = limit
        if page is not None:
            params['_page'] = page
        params.update(kwargs)
        url = "http://lda.data.parliament.uk/%s" % path
        if len(params) > 0:
            url = url + "?" + urllib.parse.urlencode(params)
        res = self.http.get(url)
        res.raise_for_status()
        data = res.json()
        return data['result']


class House(object):
    def __init__(self, name, parl):
        self.name = name
        self.parl = parl

    def recent_divisions(self, limit=50, page=0, since=None):
        res = self.parl.get("%sdivisions.json" % self.name.lower(), limit, page)
        divisions = []
        for item in res['items']:
            if since is not None and item['uin'] <= since:
                continue
            div = Division(self)
            div.title = item['title']
            div.uin = item['uin']
            div.resource = item['_about']
            div.date = parse_data(item['date']).date()
            divisions.append(div)
        # Divisions are not correctly sorted within days, so re-sort them
        return sorted(divisions)


class Commons(House):
    def __init__(self, parl):
        self.name = 'Commons'
        self.parl = parl

    def get_edms(self, limit=50, page=0):
        res = self.parl.get("edms.json", limit, page)
        for item in res['items']:
            edm = EDM()
            edm.title = item['title']
            edm.session = item['session']
            edm.number = int(parse_data(item['edmNumber']))
            edm.date_tabled = parse_data(item['dateTabled']).date()
            edm.status = parse_data(item['edmStatus'])
            if 'sponsorPrinted' in item:
                edm.sponsors = item['sponsorPrinted']
            edm.primary_sponsor = item['primarySponsorPrinted']
            edm.signatures = item['numberOfSignatures']
            yield edm
