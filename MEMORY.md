# Project Memory

## Current State

- As of 2026-08-29, the repository contains a dependency-free SVG/HTML motion asset bundle under `svg-transition/`; no application framework or package manager is established.
- `robot-a3/` is a standalone Node.js 24 TypeScript package for the Zhiyuan A3 TTS/status/stop boundary. It has zero runtime dependencies, defaults to a local mock, and is not coupled to the future application stack.
- `a3-mujoco-smoke/` is a simulation-only AimRT/MuJoCo neck-control harness. It uses loopback HTTP plus protobuf messages and remains separate from the TTS gateway and all physical-robot transports.
- `svg-transition/family-work-suite/` contains six roles with exact static family/work endpoints and two one-shot transition SVGs per role (24 SVGs total). The family forms use independent home activities rather than a child as an identity cue.

## Durable Decisions

- Add project-specific architecture, testing, and deployment decisions only after they are established.
- Record secret locations only; never record secret values.
- `ORCA_WORKTREE_LITE.md` is the source of truth for PRD-driven multi-agent development. `AGENTS.md` activates it when work can be split into genuinely independent tracks.
- Each development track uses one long-lived agent, one worktree, one branch, and mutually exclusive `write_paths`; integration happens once in a separate worktree after track-level acceptance passes.
- Keep coordination lightweight: use Git, relevant tests, and runnable behavior as evidence instead of creating custom scheduling or proof infrastructure.
- Keep AI outside the vendor protocol boundary: models may emit only the structured commands defined in `robot-a3/robot-command.schema.json`; deterministic code owns templates, A3 RPC paths, trace IDs, timeouts, serialization, and response validation.
- Real robot access is opt-in with both `ROBOT_MODE=real` and `ENABLE_ROBOT=true`. The gateway binds to loopback by default, requires a token for non-loopback binding, and intentionally excludes all motion control until separately specified and physically safety-tested.
- The supplied `aimrt_mujoco_sim_a3` archive was validated in WSL2 with the `a3_t2d5` model. Its body-drive contract uses `/body_drive/neck_joint_command`, joint order `head_yaw_joint` then `head_pitch_joint`, and iceoryx/ROS 2 message types; the smoke harness instead uses a simulation-only protobuf HTTP topic.
- The generic MuJoCo motor subscriber computes one force value per message, so a position target must be published continuously. A one-shot request leaves constant force applied and can drive a joint to a limit; the smoke controller publishes at 50 Hz and sends a zero-effort release on exit.
- Model-only neck limits are yaw `[-1.0472, 1.0472]` and pitch `[-0.436332, 0.261799]`. Do not use these as physical-robot safety limits or reuse simulation gains on hardware.
- The no-ROS build needs `libfastcdr-dev` and a local CMake repair that exposes `yaml-cpp::yaml-cpp` as a public dependency of `mujoco_sim_module`. The validated WSL run reached about `0.1117 rad` for a `0.1 rad` yaw target, but AimRT reported scheduler delay, so the evidence proves function rather than real-time performance.
- Treat the supplied A3 HandOff as product intent rather than protocol truth. The official HTTP path omits `pb:/`; `PlayTTS` includes `priority_level`, caller `trace_id`, and `is_interrupted`; status is nested at `tts_status.tts_status`; normal completion may be observed as `TTSStatusType_NOTInQue`.
- The Working Woman source is Noun Project icon 7641720 by sentya irma. Keep attribution metadata in derived assets and confirm the Creative Commons attribution requirements before external distribution.
- `svg-transition/working-woman-motion/working-woman-motion.svg` is the self-contained animated asset; `logo_motion.html` is its replayable QA showcase. The accepted vector fit uses three semantic paths and records alpha-aware IoU evidence in `outputs/`.
- The mother role under `svg-transition/working-woman-mother/` is an original derivative that preserves the working-woman head as an identity anchor. It is intentionally child-free and uses an apron, saucepan, lid, and steam to show home cooking. Its bidirectional transitions use the laptop/saucepan area as the reveal focus, and their final frames must remain pixel-identical to the static role SVGs.
- `svg-transition/family-role-suite/` extends the silhouette system with five pure-vector static roles: father/home repair, daughter/reading, son/skateboarding, grandfather/cane, and grandmother/knitting. Its preview reuses the canonical mother SVG rather than duplicating it; every role must remain distinguishable at 128 px and the 390 px preview must not overflow horizontally.
- `svg-transition/family-role-suite/generate_family_work_suite.py` is the dependency-free source of truth for the family/work deliverables. Each transition must embed markup identical to its static endpoints, support reduced motion, hold on the destination, and pass the structural, 128 px, midpoint-motion, desktop, and true 390 px CDP checks before packaging.
