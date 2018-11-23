from typing import Optional

# This is a list of all parties in the UK parliament.
# For the purposes of this list, the Co-operative Party is
# considered to be part of Labour as they vote together.
#
# (name, alternative names, abbreviation)
PARTIES = [
    ("Conservative Party", ["Conservative and Unionist Party"], "CON"),
    ("Democratic Unionist Party", [], "DUP"),
    ("Green Party", [], "GRN"),
    ("Labour Party", ["Labour (Co-op)"], "LAB"),
    ("Liberal Democrats", ["Liberal Democrat"], "LIB"),
    ("Plaid Cymru", [], "PC"),
    ("Scottish National Party", [], "SNP"),
    ("Sinn Féin", [], "SF"),
    ("Social Democratic and Labour Party", [], "SDLP"),
    ("Ulster Unionist Party", [], "UUP"),
    # Not-really-parties:
    ("Independent", [], "IND"),
    ("Crossbench", [], "XB"),
    ("Non-affiliated", [], "NA"),
    ("Bishops", [], "B"),
]


def normalise_party_name(name):
    name = name.strip().lower()
    name = name.replace(" party", "")
    return name


class Party(object):
    def __init__(self, name: str, alt_names: list, abbreviation: str):
        self.name = name
        self.alt_names = alt_names
        self.abbreviation = abbreviation

    def __repr__(self):
        return '<Party "{}">'.format(self.name)

    def __str__(self):
        return self.name


class Parties(object):
    def __init__(self, parl):
        self.parl = parl
        self.parties = []
        for party in PARTIES:
            self.parties.append(Party(*party))

    def from_name(self, name: Optional[str]) -> Optional[Party]:
        if name is None:
            return None
        for party in self.parties:
            if normalise_party_name(party.name) == normalise_party_name(name):
                return party
            for alt in party.alt_names:
                if normalise_party_name(alt) == normalise_party_name(name):
                    return party
        return None

    def all(self):
        """ Return a list of all known parties in Parliament """
        return self.parties

    def __repr__(self):
        return "<{} parties>".format(len(self.parties))
