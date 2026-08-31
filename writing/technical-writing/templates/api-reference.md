# {API name}

{What the API does and when to use it.}

## {Operation name}

```text
<signature, METHOD /path, or protocol form>
```

### Authentication and permissions

{Required identity, scope, role, or state.}

### Parameters

| Name | Location | Type | Required | Default | Description |
| --- | --- | --- | --- | --- | --- |
| `{name}` | {path/query/header/body} | `{type}` | {yes/no} | {value/none} | {Range, format, unit, and constraints.} |

### Request

```json
{
  "<field>": "<value>"
}
```

### Response

{Status, return type, and field semantics.}

```json
{
  "<field>": "<value>"
}
```

### Errors

| Error/status | Condition | Recovery |
| --- | --- | --- |
| `{error}` | {Exact trigger} | {Caller action} |

### Behavior and constraints

{Side effects, idempotency, ordering, pagination, rate limits, compatibility, or version limits. Delete items that do not apply.}

### Example

```text
<Complete, internally consistent example>
```
