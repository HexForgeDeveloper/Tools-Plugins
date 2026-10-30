feat(wirebundle): sync obstacle routing and editor UI tests from ToolsProject

Import node obstacle avoidance, bounded extra-bend routing, backward native
spline directions and a viewport-clamped shape toolbar from ToolsProject.
Keep the preview and graph commit on the same plan and reject blocked paths
before creating a transaction. Add planner, toolbar and Automation Driver
Blueprint/Material scenarios, increasing WireBundle coverage from 22 to 50 tests.

Make the Material movement test independent of saved grid preferences, restoring
those preferences afterwards. Preserve the DataAssetManager transient fixtures
and existing menu formatting. Document how the three working trees synchronize.

Validation: final isolated UE 5.5 Win64 Development build; 151/151 collection
tests passed (137 clean, 14 with warnings). FPShooterEditor Development and
DebugGame built; all 50 WireBundle integration tests passed (49 clean, 1 with
warnings). Regenerated VS2022 project files for ToolsProject and FPShooter.

Canonical ToolsProjectEditor rebuilt after the test correction, and all 50
WireBundle tests passed (49 clean, one with warnings). Regenerated its VS2022
project files after the tests. The initial canonical run exposed a preference-
dependent Material assertion and a Slate invalid-window ensure; the guarded
settings fix and final full rerun are recorded in the review report. No commit
or push was created by this synchronization task.
