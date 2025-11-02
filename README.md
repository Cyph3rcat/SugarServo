# servow — SugarServo subsystem

This folder contains the servow subsystem for the SugarServo project — a small Python-based layer that sequences servo motion, animations, and optional sound cues. The code is organized to separate high-level orchestration, motion/operation utilities, and animation helpers so you can easily test, extend, or reuse pieces in other projects.

Contents
- proton.py — main orchestrator / entrypoint for the servow system
- operationfn.py — low-level servo operation helpers and command handlers
- animatefn.py — higher-level animation/sequence helpers built on operations
- playground.py — lightweight test harness / quick interactive experiments
- keys.env — environment file for any API keys, tokens, or configuration secrets (kept out of VCS)
- servoSounds/ — directory for optional sound files used alongside animations

What this system does
- Accepts high-level animation or operation requests (sequences such as "wave", "nod", or programmatic motion patterns).
- Converts those requests into concrete servo position commands and timing using functions in operationfn.py.
- Defines reusable animation patterns and composite sequences in animatefn.py.
- Optionally plays sound cues or effects from servoSounds/ to synchronize audio with motion (if sound playback is implemented/available in your runtime).
- Provides a playground/test script (playground.py) for manual testing and quick iteration without the whole system.

How it works — component overview

1. proton.py (Orchestration)
- Acts as the top-level controller: loads configuration, validates environment (keys.env), initializes hardware or simulation backends, and invokes animations or operations.
- Typical responsibilities:
  - Read and parse environment variables (e.g., device IDs, API keys, or runtime mode flags).
  - Instantiate the servo controller or mock (hardware abstraction layer).
  - Route incoming commands (CLI, network, or scheduled) into the operation/animation layer.
- This file is the place to wire project-specific integrations (e.g., networking, voice commands, webhooks).

2. operationfn.py (Operations / Motion primitives)
- Contains the basic building blocks for commanding servos: functions that set positions, handle interpolation or easing, and manage timing.
- Implements safety checks and limits (angle ranges, speed limits), so higher-level code can rely on consistent behavior.
- Likely exposes:
  - set_servo_angle(servo_id, angle, duration)
  - move_to_positions(position_map, duration)
  - stop_all() or emergency_stop()
- Use this module when you need deterministic, low-level control.

3. animatefn.py (Animations / Sequences)
- Builds on operationfn.py to create named animations (for example: wave, nod, spin, idle-breathe).
- Coordinates multiple servos, timing, and sequencing. May include:
  - chaining of motion primitives
  - repeating loops
  - transitions and easing between keyframes
- This is where to add expressive behaviors and choreographies.

4. playground.py (Development & testing)
- Small script intended for quick experiments and manual invocation of functions from operationfn.py and animatefn.py.
- Useful for debugging servo calibration, validating timing, or trying new animation ideas without starting the whole orchestration stack.

5. keys.env
- Simple dotenv-style file to keep secrets/configuration out of source code.
- Typical values: hardware identifiers, API keys for cloud services, flags to toggle "dry-run" vs hardware mode.
- IMPORTANT: Do not commit real secrets. This file should be kept private and added to .gitignore.

6. servoSounds/
- Directory to store sound effects that can be played in sync with motion.
- The orchestrator/animations can reference files here to add audio cues to animations.

Getting started (development workflow)
1. Set up environment
- Create a local keys.env (copy keys.env.example if provided) and fill in required values (hardware port, mode=dry/hw, etc.).
- Install Python dependencies if the project has a requirements file (not included here) or use your preferred environment.

2. Calibrate hardware
- Use playground.py to call single-step operations and verify servo response:
  - Move one servo to a safe home angle
  - Check mechanical range and trim offsets

3. Run an animation
- Use proton.py (or import animatefn and operationfn in a REPL) to invoke a named animation. Example (pseudocode):
  - from animatefn import wave
  - wave(controller, repetitions=3)

4. Add or modify animations
- Implement new sequence functions in animatefn.py that compose primitives from operationfn.py.
- Keep safety and timing centralized in operationfn.py.

Notes, assumptions & extension points
- Hardware abstraction: The codebase is organized to allow a hardware controller or a mock/simulator to be swapped in. Keep device-specific code isolated so animations stay portable.
- Safety: Ensure operationfn enforces angle limits, speed constraints, and emergency stop behavior for real hardware.
- Synchronization: If you add sound playback, coordinate timing using the same scheduler used for motion to avoid drift.
- Persistence & remote control: proton.py is the natural place to add APIs, sockets, or message queues if you want to control servos remotely.

Examples (conceptual)
- wave animation:
  - animatefn.wave(controller, hand_servo_id=1, repeats=2)
  - Under the hood: a sequence of angle changes applied with small delays; uses operationfn to handle interpolation and limits.

- choreography:
  - animatefn.perform_show(controller, pattern_list)
  - Under the hood: iterate high-level patterns composed from several animatefn primitives; optionally trigger audio from servoSounds/.

Contributing
- Add new animation functions to animatefn.py and unit-test them using a mock controller that records commands.
- Keep low-level motion logic in operationfn.py; avoid duplicating interpolation/limit code.
- Use playground.py for manual verification and then integrate into proton.py for production behavior.

If you'd like, I can:
- Open a PR that adds this README.md into servow/ for you.
- Generate a starter keys.env.example with safe placeholder values.
- Inspect the actual contents of proton.py, operationfn.py, and animatefn.py and produce a more detailed README with concrete function names and examples.
