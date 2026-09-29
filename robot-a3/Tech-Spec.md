# A3 Robot Interface Technical Specification

## Architecture

```text
AI or product
  -> local JSON command API
  -> command validator and template renderer
  -> serial announcement adapter
  -> A3 HTTP JSON RPC client
  -> A3 MDU
```

`src/contracts.ts` is the single source of truth for public data contracts. `src/a3-client.ts` owns vendor-specific RPC behavior. `src/adapter.ts` owns product templates and announcement serialization. `src/ai-gateway.ts` exposes only the command allowlist. `src/server.ts` is an optional local transport.

## Vendor contract corrections

The supplied HandOff document is treated as intent, not executable truth. The official A3 documentation requires:

- URL paths such as `/rpc/aimdk.protocol.TTSService/PlayTTS`; `pb:/` is the interface name, not part of the HTTP URL.
- `priority_level`, caller-generated `trace_id`, and `is_interrupted` in `PlayTTS`.
- Status at `tts_status.tts_status`, not at the top level.
- `TTSStatusType_NOTInQue` as the usual observable terminal state because `End` is brief.

The undocumented `speaker` field is not sent.

## Safety boundaries

- `ROBOT_MODE=mock` is the default. Real calls require `ROBOT_MODE=real` and `ENABLE_ROBOT=true`.
- Only TTS, status, and stop-one-trace are implemented.
- The AI boundary accepts JSON commands, never source code, shell commands, RPC names, or arbitrary URLs.
- TTS text is produced only from fixed templates and scalar values, then checked against the 1024-byte limit.
- External responses contain stable error codes rather than raw network bodies or stack traces.
- Each HTTP call has an abort timeout; playback polling has a total deadline.
- Announcements are serialized in-process to prevent overlapping speech.
- The server binds to loopback by default. A non-loopback bind requires bearer-token authentication.

## Offline audio decision

The robot can play a PCM/WAV file only when that file already exists on the robot. This package does not invent silent or synthetic placeholder media. A future deployment step may upload approved audio and then add a narrowly configured `PlayMediaFile` fallback.

## Verification

- `npm run typecheck`
- `npm test`
- `npm run smoke`
- `npm run check`

