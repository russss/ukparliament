A client for the [UK parliament API](http://www.data.parliament.uk/).

# Example

```python
from ukparliament import Parliament
parliament = Parliament()
parliament.commons.recent_divisions(limit=4)
```
    [<Commons division: "European Union (Notification of Withdrawal) Bill: Programme" on 2017-02-01>,
     <Commons division: "European Union (Notification of Withdrawal) Bill: Second Reading" on 2017-02-01>,
     <Commons division: "European Union (Notification Etc.) Bill: Second Reading - Mr Robertson's Amendment" on 2017-02-01>,
     <Commons division: "Opposition Motion: Prisons" on 2017-01-25>]
