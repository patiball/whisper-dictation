## ADDED Requirements
### Requirement: Supervisor-Controlled Worker Runtime
The system SHALL provide a dedicated supervisor process that manages dictation worker lifecycle independently from worker execution.

#### Scenario: Supervisor starts worker
- **WHEN** supervisor process starts with a valid worker profile
- **THEN** it launches a worker subprocess with the selected backend/model profile
- **AND** it records worker startup in supervisor logs

#### Scenario: Supervisor stops worker
- **WHEN** user triggers stop from supervisor controls
- **THEN** supervisor terminates the worker process gracefully
- **AND** it does not auto-restart the worker after intentional stop

### Requirement: Headless Worker Mode
The worker runtime SHALL support explicit runtime mode selection so a worker can run without tray UI when controlled by supervisor.

#### Scenario: Headless worker on Windows
- **WHEN** worker is started with runtime mode `headless`
- **THEN** it runs without creating a tray icon
- **AND** existing recording/transcription flow remains functional

### Requirement: Profile Switching by Controlled Restart
The supervisor SHALL switch backend/model profiles by restarting the worker process with new launch arguments.

#### Scenario: Switch from whispercpp to python profile
- **WHEN** a python profile is selected in supervisor controls
- **THEN** supervisor stops the current worker and starts a new worker with `--backend python`
- **AND** the new worker uses the selected python model argument

### Requirement: Bounded Crash Auto-Restart
The supervisor SHALL auto-restart the worker only for unexpected exits and SHALL enforce a configured retry limit.

#### Scenario: Unexpected worker crash
- **WHEN** worker exits unexpectedly while supervisor policy allows retries
- **THEN** supervisor starts worker again after a cooldown delay
- **AND** increments restart attempt counter

#### Scenario: Retry limit reached
- **WHEN** worker repeatedly crashes and reaches configured retry limit
- **THEN** supervisor stops auto-restart attempts
- **AND** logs that the retry limit was reached
