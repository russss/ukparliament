from functools import total_ordering
from dateutil.parser import parse as parse_date
from collections import defaultdict


def parse_data(data):
    if type(data) == list:
        data = data[0]
    if "_datatype" in data:
        if data["_datatype"] == "dateTime":
            return parse_date(data["_value"])
    else:
        return data["_value"]


def parse_date_element(el):
    if not el.text:
        return None
    return parse_date(el.text)


class Resource(object):
    def __init__(self):
        self.resource = None

    @property
    def resource_id(self):
        return int(self.resource.split("/")[-1])


@total_ordering
class Division(Resource):
    def __init__(self, house):
        super().__init__()
        self.house = house
        self.parl = house.parl
        self._data_fetched = False
        self.title = None
        self.uin = None
        self.date = None

    def _fetch_data(self):
        res = self.parl.get(
            "%sdivisions/id/%s.json" % (self.house.name.lower(), self.resource_id)
        )
        data = res["primaryTopic"]
        if self.house.name == "Commons":
            self.abstain = int(parse_data(data["AbstainCount"]))
            self.ayes = int(parse_data(data["AyesCount"]))
            self.did_not_vote = int(parse_data(data["Didnotvotecount"]))
            self.error_vote = int(parse_data(data["Errorvotecount"]))
            self.margin = int(parse_data(data["Margin"]))
            self.noes = int(parse_data(data["Noesvotecount"]))
            self.non_eligible = int(parse_data(data["Noneligiblecount"]))
            self.suspended_expelled = int(
                parse_data(data["Suspendedorexpelledvotescount"])
            )
            self.votes = {"aye": MemberList(), "no": MemberList()}
            for vote in data["vote"]:
                member = self.house.members.from_vote(vote)

                if vote["type"] == "http://data.parliament.uk/schema/parl#AyeVote":
                    self.votes["aye"].append(member)
                elif vote["type"] == "http://data.parliament.uk/schema/parl#NoVote":
                    self.votes["no"].append(member)

        elif self.house.name == "Lords":
            self.contents = int(data["officialContentsCount"])
            self.not_contents = int(data["officialNotContentsCount"])
            self.votes = {"content": MemberList(), "not_content": MemberList()}
            for vote in data["vote"]:
                member = self.house.members.from_vote(vote)

                if vote["type"] == "http://data.parliament.uk/schema/parl#ContentVote":
                    self.votes["content"].append(member)
                elif (
                    vote["type"]
                    == "http://data.parliament.uk/schema/parl#NotContentVote"
                ):
                    self.votes["not_content"].append(member)
        self._data_fetched = True

    @property
    def passed(self):
        if self.house.name == "Commons":
            return self.ayes > self.noes
        elif self.house.name == "Lords":
            return self.contents > self.not_contents

    def __eq__(self, other):
        return type(other) == type(self) and other.uin == self.uin

    def __gt__(self, other):
        if self.date == other.date:
            return other.uin > self.uin
        return other.date > self.date

    def __repr__(self):
        return '<%s division: "%s" on %s>' % (self.house.name, self.title, self.date)

    def __getattr__(self, name: str):
        if not self._data_fetched:
            self._fetch_data()
            res = getattr(self, name)
            if res is None:
                raise AttributeError()
            return res
        raise AttributeError()


class EDM(Resource):
    def __repr__(self):
        return '<EDM %s: "%s">' % (self.number, self.title)


class Bill(Resource):
    def __init__(self, parl):
        self.parl = parl
        self.title = None
        self.home_page = None
        self.type = None
        self.date = None

    def fetch_data(self):
        res = self.parl.get("bills/%s.json" % self.resource_id)["primaryTopic"]
        self.description = res["description"]

    def __repr__(self):
        return '<Bill "%s" (%s)>' % (self.title, self.date)


class Member(Resource):
    def __init__(self, parl, house, member_id):
        self.house = house
        self.id = member_id
        self.parl = parl
        self.display_name = None
        self.party = None
        self._data_fetched = False

    def _fetch_data(self):
        data = self.parl.get_members(id=self.id)
        mem = data.find("Member")
        if mem is None:
            raise ValueError("Unable to load data for member with id %s!" % self.id)
        self._populate_data(mem)

    def _populate_data(self, data):
        self.dods_id = int(data.get("Dods_Id"))
        self.pims_id = int(data.get("Pims_Id"))
        self.display_name = data.find("DisplayAs").text
        self.party = self.parl.parties.from_name(data.find("Party").text)
        self.full_name = data.find("FullTitle").text
        self.date_of_birth = parse_date_element(data.find("DateOfBirth"))
        self.start_date = parse_date_element(data.find("HouseStartDate"))
        self.end_date = parse_date_element(data.find("HouseEndDate"))
        self.gender = data.find("Gender").text
        if self.house.name == "Commons":
            self.constituency = data.find("MemberFrom").text
        else:
            # The type of peer is in the MemberFrom field here..
            self.member_type = data.find("MemberFrom").text
        self._data_fetched = True

    def __repr__(self):
        return "<Member ({}) #{} {} ({})>".format(
            self.house.name, self.id, self.display_name, self.party
        )

    def __getattr__(self, name: str):
        if not self._data_fetched:
            self._fetch_data()
            res = getattr(self, name)
            if res is None:
                raise AttributeError()
            return res
        raise AttributeError()


class MemberList(list):
    def by_party(self):
        bp = defaultdict(lambda: 0)
        for item in self:
            bp[item.party] += 1
        return dict(bp)
