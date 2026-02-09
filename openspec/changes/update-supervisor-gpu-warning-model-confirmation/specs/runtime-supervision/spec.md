## ADDED Requirements
### Requirement: Runtime Model and Acceleration Confirmation
The system SHALL report the model actually used by whisper.cpp and the inferred acceleration state for each transcription run.

#### Scenario: whisper.cpp transcription completes
- **WHEN** whisper.cpp returns transcription output
- **THEN** worker emits a machine-readable status line with model and acceleration fields
- **AND** worker prints a human-readable confirmation line with model and acceleration summary

### Requirement: Supervisor CPU/Fallback Warning
The supervisor SHALL warn when selected whisper.cpp profile is likely to run without expected OpenVINO GPU acceleration.

#### Scenario: Missing OpenVINO encoder artifacts
- **WHEN** selected whisper.cpp model lacks required `*-encoder-openvino.xml/.bin` files and OpenVINO GPU mode is requested
- **THEN** supervisor records a warning state
- **AND** the warning is visible in supervisor status output

#### Scenario: Worker reports CPU fallback
- **WHEN** worker emits status line indicating `cpu_fallback`
- **THEN** supervisor updates current worker status to warning state
- **AND** warning remains visible until profile restart or new status update
