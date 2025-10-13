Rules 


| Type          | Description                         | Example                                                      |
| ------------- | ----------------------------------- | ------------------------------------------------------------ |
| `exact_match` | Field must match value exactly      | `{"type": "exact_match", "value": "Administrative Officer"}` |
| `one_of`      | Field must be one of allowed values | `["Mauritian", "Permanent Resident"]`                        |
| `not_in`      | Value must not appear in list       | `["Suspended", "Dismissed"]`                                 |
| `regex`       | Validate using regex pattern        | Email, phone number                                          |
| `range`       | Numeric range constraint            | `{"min": 25, "max": 40}`                                     |
| `min` / `max` | Minimum or maximum only             | `{"min": 2}` years experience                                |
| `boolean`     | Must be true or false               | `{"type": "boolean", "value": false}`                        |
| `exists`      | Field must be present/non-null      | `{"type": "exists"}`                                         |
| `not_exists`  | Field must be null/missing          | For fields like `court_conviction`                           |


