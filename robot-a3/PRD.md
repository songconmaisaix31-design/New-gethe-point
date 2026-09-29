# A3 Robot Interface MVP

## Goal

Deliver a standalone interface that lets an AI-enabled application request a small, safe set of Zhiyuan A3 audio actions without coupling the robot protocol to the unfinished product.

## Core acceptance path

1. Start the service in mock mode with no robot connected.
2. Submit a structured `speak` command using an allowlisted template.
3. Render and validate the text, call `PlayTTS`, poll `GetAudioStatus`, and return a stable delivery result.
4. Query or stop a known trace ID through the same stable API.
5. Switch to a real A3 only through explicit environment configuration.

## Users and value

- Product developers get a stable integration boundary while the main application is still changing.
- Demo operators get deterministic enable/disable and stop controls.
- End users are protected from arbitrary model-generated robot commands and overlapping announcements.

## In scope

- A3 standard HTTP JSON RPC for TTS, status, and stopping one trace.
- Structured AI command gateway with an action allowlist.
- Local HTTP service and programmatic package API.
- Mock mode, tests, smoke command, and operator runbook.

## Out of scope

- Neck, joint, locomotion, navigation, camera, microphone, or autonomous motion control.
- Direct integration with a specific LLM provider or the unfinished main product.
- Database persistence and `NotificationLog` ownership.
- Fabricating or uploading fallback PCM files.
- Claims of real-hardware validation without an A3 on the same network.

## Acceptance criteria

- Runtime dependencies are zero and Node.js 24 is supported.
- The service binds to `127.0.0.1` by default and uses mock mode by default.
- Non-loopback binding is rejected unless a gateway token is configured.
- Unknown actions, templates, fields, malformed responses, oversized text, and timeouts fail closed.
- TTS calls use the official A3 RPC URL and request shape.
- Successful playback recognizes both the brief `End` state and the normal terminal `NOTInQue` state.
- Concurrent `speak` commands are serialized; `stop` remains immediately available.
- Unit and local mock integration tests pass without a robot.

