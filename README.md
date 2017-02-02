[![PyPI version](https://badge.fury.io/py/ukparliament.svg)](https://badge.fury.io/py/ukparliament)

A client for the [UK Parliament API](http://www.data.parliament.uk/).
Python 3 only, contributions welcome.

Currently supports:
* Commons and Lords divisions
* Early Day Motions

# Installing

    pip install ukparliament

# Example

```python
from ukparliament import Parliament
parliament = Parliament()
divisions = parliament.commons.recent_divisions(limit=4)
print(divisions)
```
    [<Commons division: "European Union (Notification of Withdrawal) Bill: Programme" on 2017-02-01>,
     <Commons division: "European Union (Notification of Withdrawal) Bill: Second Reading" on 2017-02-01>,
     <Commons division: "European Union (Notification Etc.) Bill: Second Reading - Mr Robertson's Amendment" on 2017-02-01>,
     <Commons division: "Opposition Motion: Prisons" on 2017-01-25>]
