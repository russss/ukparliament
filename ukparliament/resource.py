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


class Resource(object):
    @property
    def resource_id(self):
        return int(self.resource.split("/")[-1])


@total_ordering
class Division(Resource):
    def __init__(self, house):
        self.house = house
        self.parl = house.parl
        self.data_fetched = False

    def fetch_data(self):
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
        self.data_fetched = True

    @property
    def passed(self):
        if self.house.name == "Commons":
            return self.ayes > self.noes
        elif self.house.name == "Lords":
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


class EDM(Resource):
    def __repr__(self):
        return '<EDM %s: "%s">' % (self.number, self.title)


class Bill(Resource):
    def __init__(self, parl):
        self.parl = parl

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

    def __repr__(self):
        if getattr(self, "display_name"):
            return "<Member ({}) {} (ID {})>".format(
                self.house.name, self.display_name, self.id
            )

        return "<Member %s>" % self.id


class MemberList(list):
    def by_party(self):
        bp = defaultdict(lambda: 0)
        for item in self:
            bp[item.party] += 1
        return dict(bp)
