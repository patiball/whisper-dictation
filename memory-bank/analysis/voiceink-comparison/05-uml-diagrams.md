# UML Specifications for whisper-dictation (To-Be)

## Context for AI Agents
This document provides detailed UML specifications for the target (To-Be) architecture of `whisper-dictation`. It includes diagrams generated with both PlantUML (for static structure) and Mermaid (for dynamic behavior), adhering to the complexity limits defined in the analysis framework.

## 1. Use Case Diagram (PlantUML)
Describes the main interactions between the user and the system.

![Use Case Diagram](05-diagrams/use-case.png)
*Source: [use-case.puml](05-diagrams/use-case.puml)*

## 2. Component Diagram (PlantUML)
Shows the high-level components of the system and their relationships.

![Component Diagram](05-diagrams/component.png)
*Source: [component.puml](05-diagrams/component.puml)*

## 3. Deployment Diagram (PlantUML)
Illustrates the deployment of the application on target platforms.

![Deployment Diagram](05-diagrams/deployment.png)
*Source: [deployment.puml](05-diagrams/deployment.puml)*

## 4. Package Diagram (PlantUML)
Shows the organization of the codebase into high-level packages.

![Package Diagram](05-diagrams/package.png)
*Source: [package.puml](05-diagrams/package.puml)*

## 5. Class Diagram: Plugin System (PlantUML)
Details the class structure of the proposed plugin system.

![Plugin System Classes](05-diagrams/plugin-classes.png)
*Source: [plugin-classes.puml](05-diagrams/plugin-classes.puml)*

## 6. Sequence Diagram: Plugin Processing Flow (Mermaid)
Shows the sequence of interactions when processing a transcript through the plugin system.

```mermaid
sequenceDiagram
    participant TE as Transcription Engine
    participant PM as Plugin Manager
    participant P1 as Plugin: Timestamps
    participant P2 as Plugin: Custom Vocab
    participant O as Output
    
    TE->>PM: raw_transcript
    PM->>PM: Get enabled plugins
    
    PM->>P1: process(transcript)
    P1-->>PM: transcript_with_time
    
    PM->>P2: process(transcript_with_time)
    P2-->>PM: final_transcript
    
    PM->>O: final_transcript
```

## 7. State Diagram: Recording Lifecycle (Mermaid)
Describes the various states of the application as it relates to recording.

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Initializing : User starts recording
    Initializing --> Recording : Audio input ready
    Initializing --> Error : Init failed
    
    Recording --> Stopping : User stops
    
    Stopping --> Processing : Finalizing transcript
    Processing --> Idle : Processing complete
    
    Error --> Idle : User acknowledges
```

## Quality Checklist
- [x] Durability: No brittle references
- [x] Diagram-first: Visual representations included
- [x] Self-contained: Context for agents present
- [x] Cross-linked: References to other analysis files (to be added)
