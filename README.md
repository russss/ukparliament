[![PyPI version](https://badge.fury.io/py/ukparliament.svg)](https://badge.fury.io/py/ukparliament)

A client for the [UK Parliament API](http://www.data.parliament.uk/).
Python 3 only, contributions welcome.

Currently supports:
* Commons and Lords divisions
* Commons and Lords membership
* Early Day Motions

# Installing

The package can be installed in the usual way with pip:

    pip install ukparliament

# Examples
Firstly, import and create the client:

```python
>>> from ukparliament import Parliament
>>> parliament = Parliament()
```

Getting membership of houses:

```python
>>> mps = parliament.commons.members.current()
>>> len(mps)
650
```

Lists of members can be broken down by party, but otherwise behave as normal Python lists:

```python
>>> mps.by_party()
{<Party "Labour Party">: 257,
 <Party "Conservative Party">: 315,
 <Party "Scottish National Party">: 35,
 <Party "Sinn Féin">: 7,
 None: 1,
 <Party "Liberal Democrats">: 12,
 <Party "Democratic Unionist Party">: 10,
 <Party "Plaid Cymru">: 4,
 <Party "Independent">: 8,
 <Party "Green Party">: 1}
```

Fetching divisions for a house:

```python
>>> divisions = parliament.commons.recent_divisions(limit=4)
>>> division = divisions[0]
>>> division
<Commons division: "draft Double Taxation Relief and International Tax Enforcement (Jersey) Order 2018" on 2018-11-21>
```

Divisions contain vote totals:

```python
>>> division.ayes, division.noes, division.passed
(302, 238, True)
```

You can also get the full lists of who voted:

```python
>>> division.votes['aye'].by_party()
{<Party "Conservative Party">: 293,
 <Party "Independent">: 3,
 <Party "Democratic Unionist Party">: 6}
```
