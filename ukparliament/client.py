import urllib.parse
import requests
import datetime
import re

from .resource import Bill, EDM, Division, Member, parse_data
from .parties import Parties


class Parliament(object):
    def __init__(self):
        self.http = requests.Session()
        self.commons = Commons(self)
        self.lords = House("Lords", self)
        self.parties = Parties(self)

    def get_bills(self, limit=50, page=0):
        res = self.get("bills.json", limit, page)
        for item in res["items"]:
            b = Bill(self)
            b.resource = item["_about"]
            b.title = item["title"]
            b.home_page = item["homePage"]
            b.type = item["billType"]
            b.date = parse_data(item["date"]).date()
            yield b

    def get(self, path, limit=None, page=None, additional_params={}):
        params = {}
        if limit is not None:
            params["_pageSize"] = limit
        if page is not None:
            params["_page"] = page
        params.update(additional_params)
        url = "http://lda.data.parliament.uk/%s" % path
        if len(params) > 0:
            url = url + "?" + urllib.parse.urlencode(params)
        res = self.http.get(url)
        res.raise_for_status()
        data = res.json()
        return data["result"]


class Members(object):
    def __init__(self, house):
        self.parl = house.parl
        self.house = house
        self._members = {}

    def from_id(self, member_id: int) -> Member:
        if member_id not in self._members:
            self._members[member_id] = Member(self.parl, self.house, member_id)

        return self._members[member_id]

    def from_url(self, url: str) -> Member:
        """ Return a member from a data URL, e.g. http://data.parliament.uk/members/4637
        """
        res = re.match(r"^http://data.parliament.uk/members/([0-9]+)$", url)
        if not res:
            raise ValueError("Invalid member URL: %s" % url)
        return self.from_id(int(res.groups(1)[0]))

    def from_vote(self, data: dict):
        """ Return a member from a short summary of that member, importing name and party
            from the summary to reduce additional requests.
        """
        member = self.from_url(data["member"][0]["_about"])
        member.display_name = data["memberPrinted"]["_value"]
        member.party = self.parl.parties.from_name(data["memberParty"])
        return member


class House(object):
    def __init__(self, name, parl):
        self.name = name
        self.parl = parl
        self.members = Members(self)

    def get_members(self, limit=50, page=0):
        res = self.parl.get("%smembers.json" % self.name.lower(), limit, page)
        for item in res["items"]:
            m = Member()
            m.full_name = parse_data(item["fullName"])
            yield m

    def recent_divisions(
        self, limit: int = 50, page: int = 0, since: str = None, cachebust: bool = False
    ):
        """ Return the recent divisions for this house.

            The "cachebust" parameter will defeat the rather overzealous
            caching on this endpoint, so use it considerately.
        """
        params = {}
        if since:
            params["min-uin"] = since

        if cachebust:
            params["max-date"] = datetime.datetime.utcnow().isoformat()

        res = self.parl.get("%sdivisions.json" % self.name.lower(), limit, page, params)
        divisions = []
        for item in res["items"]:
            if since is not None and item["uin"] <= since:
                continue
            div = Division(self)
            div.title = item["title"]
            div.uin = item["uin"]
            div.resource = item["_about"]
            div.date = parse_data(item["date"]).date()
            divisions.append(div)
        # Divisions are not correctly sorted within days, so re-sort them
        return sorted(divisions)


class Commons(House):
    def __init__(self, parl):
        super().__init__("Commons", parl)

    def get_edms(self, limit=50, page=0):
        res = self.parl.get("edms.json", limit, page)
        for item in res["items"]:
            edm = EDM()
            edm.title = item["title"]
            edm.session = item["session"]
            edm.number = int(parse_data(item["edmNumber"]))
            edm.date_tabled = parse_data(item["dateTabled"]).date()
            edm.status = parse_data(item["edmStatus"])
            if "sponsorPrinted" in item:
                edm.sponsors = item["sponsorPrinted"]
            edm.primary_sponsor = item["primarySponsorPrinted"]
            edm.signatures = item["numberOfSignatures"]
            yield edm
