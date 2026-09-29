# A3 MuJoCo Neck Smoke Test

This harness validates a simulation-only neck control loop without coupling motion code to `robot-a3`.

## Scope and acceptance

- Load the `a3_t2d5` model in MuJoCo through AimRT.
- Accept protobuf `JointCommandArray` messages over loopback HTTP.
- Publish and echo protobuf `JointStateArray` state.
- Hold `head_yaw_joint` near `0.1 rad` while the controller is active.
- Never connect to a physical robot or reuse these gains as real-robot safety limits.

The validated WSL run reached approximately `0.1117 rad` for a `0.1 rad` yaw target. The simulator was not real-time: AimRT reported scheduler delays, so this is functional evidence, not timing or controller-tuning evidence.

## Current local runtime

The extracted and built simulator is outside this repository:

```text
/root/orca-sim-a3/aimrt_mujoco_sim_a3/build-local
```

Copy `a3_t2d5_pb_smoke_cfg.yaml` and the two JSON payloads into that directory. Start AimRT from the same directory:

```bash
export LD_LIBRARY_PATH=.:/root/orca-sim-a3/install/lib
./aimrt_main --cfg_file_path=./a3_t2d5_pb_smoke_cfg.yaml
```

In a second WSL terminal, run the controller for a bounded smoke test:

```bash
python3 /mnt/c/Users/DW/orca/New-gethe-point/a3-mujoco-smoke/neck_controller.py --duration 20
```

Use `--duration 0` to hold the target until `Ctrl+C`. The controller sends a zero-effort release message before exiting.

## Important protocol facts

- Command topic: `/sim/a3/neck_joint_command`
- State topic: `/sim/a3/neck_joint_state`
- Message type: `pb:aimrt.protocols.sensor.JointCommandArray`
- Joint order: `head_yaw_joint`, then `head_pitch_joint`
- Model-only limits: yaw `[-1.0472, 1.0472]`, pitch `[-0.436332, 0.261799]`
- The generic motor adapter computes one force value per received message. Position holding therefore requires continuous command publication.

The archive's official body-drive path uses iceoryx/ROS 2 types and is not exercised by this smoke test. This protobuf HTTP route is intentionally simulation-only.

## Known upstream build issue

The no-ROS build requires `libfastcdr-dev`. It also needs `yaml-cpp::yaml-cpp` to be a `PUBLIC` dependency of `mujoco_sim_module`, because headers included by `mujoco_sim_pkg` reference yaml-cpp. The local extracted copy contains that one-line CMake repair; the source archive remains unchanged.
