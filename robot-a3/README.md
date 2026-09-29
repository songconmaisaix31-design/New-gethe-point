# A3 Robot Interface

Standalone, runtime-dependency-free adapter and local gateway for Zhiyuan A3 TTS control. It is deliberately limited to speech, playback status, and stopping one trace. It does not expose motion control.

## Requirements

- Node.js 24+
- npm 11+
- For real mode: an A3 running a compatible AimDK version and network access to its MDU

## Local mock quick start

```bash
npm install
npm run check
npm start
```

Then submit a structured command:

```bash
curl -X POST http://127.0.0.1:8787/v1/robot/commands \
  -H "Content-Type: application/json" \
  -d '{"action":"speak","template":"care_reminder","data":{"title":"血压药","instruction":"请在饭后服用"},"priority":"normal"}'
```

Mock mode is the default and does not contact a robot.

## Real A3 mode

Copy `.env.example` to `.env` and set:

```text
ROBOT_MODE=real
ENABLE_ROBOT=true
ROBOT_BASE_URL=http://10.42.10.10:59301
```

Do not commit `.env`. Start with `npm start`, submit one short low-priority test message, confirm physical audio, then test status and stop. The operator must remain able to mute or disable the robot.

## AI integration

Give the model [robot-command.schema.json](./robot-command.schema.json), then send its validated JSON to `POST /v1/robot/commands`. Do not give the model the robot base URL or a generic RPC tool. Application code can also import `createAiGateway` from `src/index.ts` and skip HTTP entirely.

## Demo runbook

1. Confirm the robot model and AimDK version in AimMaster.
2. Confirm the development machine can reach the MDU address.
3. Keep `ROBOT_MODE=mock` and run `npm run check`.
4. Set real mode only while an operator is present.
5. Send one neutral test announcement; verify audible output and terminal status.
6. Exercise `stop` with a longer neutral test announcement.
7. Run the care reminder scenario. Keep App notification as the operational fallback.
8. If any response is malformed, delayed, repeated, or unexpectedly loud, set `ENABLE_ROBOT=false` and restart the gateway.

## Known limitations

- Local tests prove the adapter contract and mock end-to-end flow, not compatibility with a specific physical robot firmware.
- In-memory serialization is per process. Run one gateway instance for a demo unless a shared queue is added by the future host application.
- Offline media playback requires approved PCM/WAV files to be installed on the robot first and is not included in this MVP.
- Persistence belongs to the future host application; this package returns stable results but does not own `NotificationLog`.
