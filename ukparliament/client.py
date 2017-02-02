from functools import total_ordering
import requests
from dateutil.parser import parse as parse_date


def parse_data(data):
    if type(data) == list:
        data = data[0]
    if '_datatype' in data:
        if data['_datatype'] == 'dateTime':
            return parse_date(data['_value'])
    else:
        return data['_value']


class Parliament(object):
    def __init__(self):
        self.http = requests.Session()

    @property
    def commons(self):
        return Commons(self)

    @property
    def lords(self):
        return House("Lords", self)

    def get(self, path):
        res = self.http.get("http://lda.data.parliament.uk/%s" % path)
        res.raise_for_status()
        data = res.json()
        return data['result']


class House(object):
    def __init__(self, name, parl):
        self.name = name
        self.parl = parl

    def recent_divisions(self, limit=50, page=0, since=None):
        res = self.parl.get("%sdivisions.json?_pageSize=%s&_page=%s" % (self.name.lower(), limit, page))
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
        res = self.parl.get("edms.json?_pageSize=%s&_page=%s" % (limit, page))
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


@total_ordering
class Division(object):
    def __init__(self, house):
        self.house = house
        self.parl = house.parl
        self.data_fetched = False

    def fetch_data(self):
        div_id = self.resource.split('/')[-1]
        res = self.parl.get("%sdivisions/id/%s.json" % (self.house.name.lower(), div_id))
        data = res['primaryTopic']
        if self.house.name == 'Commons':
            self.abstain = int(parse_data(data['AbstainCount']))
            self.ayes = int(parse_data(data['AyesCount']))
            self.did_not_vote = int(parse_data(data['Didnotvotecount']))
            self.error_vote = int(parse_data(data['Errorvotecount']))
            self.margin = int(parse_data(data['Margin']))
            self.noes = int(parse_data(data['Noesvotecount']))
            self.non_eligible = int(parse_data(data['Noneligiblecount']))
            self.suspended_expelled = int(parse_data(data['Suspendedorexpelledvotescount']))
        elif self.house.name == 'Lords':
            self.contents = int(data['officialContentsCount'])
            self.not_contents = int(data['officialNotContentsCount'])
        self.data_fetched = True

    @property
    def passed(self):
        if self.house.name == 'Commons':
            return self.ayes > self.noes
        elif self.house.name == 'Lords':
            return self.contents > self.not_contents

    def __getattr__(self, name):
        if not self.data_fetched:
            self.fetch_data()
            res = getattr(self, name)
            if res is None:
                raise AttributeError()
            return res
        raise AttributeError()

    def __eq__(self, other):
        return type(other) == type(self) and other.uin == self.uin

    def __gt__(self, other):
        return other.uin > self.uin

    def __repr__(self):
        return '<%s division: "%s" on %s>' % (self.house.name, self.title, self.date)


class EDM(object):
    def __repr__(self):
        return '<EDM %s: "%s">' % (self.number, self.title)
