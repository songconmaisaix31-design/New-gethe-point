# A3 Robot Gateway API Contract

## HTTP transport

- Default address: `http://127.0.0.1:8787`
- Content type: `application/json`
- Maximum request body: 32 KiB
- Authentication: optional on loopback; required for non-loopback binding using `Authorization: Bearer <token>`

## Health

`GET /health`

```json
{
  "ok": true,
  "mode": "mock",
  "robotEnabled": false
}
```

## Execute command

`POST /v1/robot/commands`

### Speak

```json
{
  "action": "speak",
  "template": "care_reminder",
  "data": {
    "title": "Blood pressure medicine",
    "instruction": "Take it after the meal"
  },
  "priority": "normal"
}
```

Allowed templates and required fields:

| Template | Required fields |
| --- | --- |
| `care_reminder` | `title`, `instruction` |
| `escalation` | `subjectName`, `title` |
| `handover_confirm` | `domainName` |

Success:

```json
{
  "ok": true,
  "action": "speak",
  "traceId": "gethepoint-...",
  "terminalStatus": "TTSStatusType_NOTInQue"
}
```

### Status

```json
{ "action": "status", "traceId": "gethepoint-..." }
```

### Stop

```json
{ "action": "stop", "traceId": "gethepoint-..." }
```

## Errors

Errors use a stable code and do not expose robot response bodies:

```json
{
  "ok": false,
  "error": "INVALID_COMMAND"
}
```

Possible codes include `INVALID_COMMAND`, `UNAUTHORIZED`, `ROBOT_DISABLED`, `TTS_TEXT_TOO_LONG`, `ROBOT_UNREACHABLE`, `ROBOT_PROTOCOL_ERROR`, `PLAYBACK_ERROR`, and `PLAYBACK_TIMEOUT`.

