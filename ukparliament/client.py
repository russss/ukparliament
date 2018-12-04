import urllib.parse
import requests
import datetime
import xml.etree.ElementTree as ET

from .resource import Bill, EDM, Division, Member, parse_data, MemberList
from .parties import Parties


class Parliament(object):
    LDA_ENDPOINT = "http://lda.data.parliament.uk/"
    MEMBERS_NAMES_ENDPOINT = (
        "http://data.parliament.uk/membersdataplatform/services/mnis/members/query/"
    )

    def __init__(self):
        self.http = requests.Session()
        self.commons = Commons(self)
        self.lords = House("Lords", self)
        self.parties = Parties(self)

    def get_bills(self, limit: int = 50, page: int = 0):
        res = self.get("bills.json", limit, page)
        for item in res["items"]:
            b = Bill(self)
            b.resource = item["_about"]
            b.title = item["title"]
            b.home_page = item["homePage"]
            b.type = item["billType"]
            b.date = parse_data(item["date"]).date()
            yield b

    def get(self, path: str, limit: int = None, page: int = None, additional_params={}):
        """ Make a request to the Linked Data API. Returns a python data structure. """
        params = {}
        if limit is not None:
            params["_pageSize"] = limit
        if page is not None:
            params["_page"] = page
        params.update(additional_params)
        url = self.LDA_ENDPOINT + path
        if len(params) > 0:
            url = url + "?" + urllib.parse.urlencode(params)
        res = self.http.get(url)
        res.raise_for_status()
        data = res.json()
        return data["result"]

    def get_members(self, **kwargs):
        """ Make a request to the Members Names API with the kwargs as parameters.
            Parameter documentation: http://data.parliament.uk/membersdataplatform/memberquery.aspx
            Returns an etree object of the XML
        """
        url = self.MEMBERS_NAMES_ENDPOINT
        url += "|".join(k + "=" + str(v) for k, v in kwargs.items())
        res = self.http.get(url)
        return ET.fromstring(res.text)


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
        """ Return a member from a data URL, e.g.:
            Commons: http://data.parliament.uk/members/4637
            Lords: http://data.parliament.uk/resources/members/api/lords/id/631
            (why are they different?)
        """
        return self.from_id(int(url.split("/")[-1]))

    def from_vote(self, data: dict) -> Member:
        """ Return a member from a short summary of that member, importing name and party
            from the summary to reduce additional requests.
        """
        if type(data["member"][0]) == dict:
            # Commons
            member = self.from_url(data["member"][0]["_about"])
        else:
            # Lords
            member = self.from_url(data["member"][0])

        if "memberPrinted" in data:
            # Commons
            member.display_name = data["memberPrinted"]["_value"]
        else:
            # Lords
            member.display_name = data["memberRank"] + " " + data["memberTitle"]

        member.party = self.parl.parties.from_name(data["memberParty"])
        return member

    def current(self) -> MemberList:
        """ Fetch all current members of the house. """
        data = self.parl.get_members(house=self.house.name)
        members = MemberList()
        for mem in data.iter("Member"):
            obj = self.from_id(int(mem.get("Member_Id")))
            obj._populate_data(mem)
            members.append(obj)
        return members


class House(object):
    def __init__(self, name: str, parl):
        self.name = name
        self.parl = parl
        self.members = Members(self)

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
            params["max-date"] = (
                datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            ).isoformat()

        res = self.parl.get("%sdivisions.json" % self.name.lower(), limit, page, params)
        divisions = []
        for item in res["items"]:
            if since is not None and item["uin"] <= since:
                continue
            div = Division(self)
            div.title = item["title"].strip()
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
