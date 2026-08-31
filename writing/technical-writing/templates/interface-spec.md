# {Interface name} specification

## Scope

{Boundary, purpose, participating components, and excluded behavior.}

## Roles and ownership

| Role/component | Responsibility | Owns/controls |
| --- | --- | --- |
| {name} | {behavior} | {resource, signal, buffer, or state} |

## Interface definition

{Endpoint, connector, bus, protocol, ABI, message channel, or signal group.}

### Data, messages, or signals

| Name | Direction | Type/width | Unit/encoding | Required/reset | Description |
| --- | --- | --- | --- | --- | --- |
| `{name}` | {in/out/bidirectional} | {type or bits} | {unit, encoding, or level} | {value} | {Semantics and constraints} |

### Timing and state

{Sequence, state machine, setup/hold, timeout, retry, flow control, and reset behavior.}

### Errors and recovery

| Condition | Detection | Required behavior | Recovery |
| --- | --- | --- | --- |
| {condition} | {signal/status/error} | {normative response} | {re-entry or reset} |

## Compatibility and versioning

{Negotiation, backward compatibility, reserved values, and deprecation.}

## Security and safety

{Authentication, authorization, trust boundary, electrical protection, or hazardous states. Delete if not applicable.}

## Conformance verification

- {Requirement} → {Observable test and pass criterion}
