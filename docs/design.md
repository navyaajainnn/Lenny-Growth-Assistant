# Design

## Principles

The research desk is quiet, editorial, and work-focused. It prioritizes source traceability, readable long-form answers, obvious system status, and a short path from question to useful artifact.

## Information architecture

The primary view has two working areas: conversation on the left and Artifact Viewer on the right. The top bar exposes local-model status. Sources stay attached to assistant responses rather than becoming a separate navigation task.

## Interaction states

- Connecting: session creation is in progress.
- Empty: a short prompt invites the first question.
- Thinking: the assistant activity indicator is visible while the request runs.
- Error: provider/database failures appear inline without losing the conversation.
- Artifact ready: the viewer shows rendered Markdown or sandboxed HTML.

## Responsive behavior

Desktop uses a two-column workspace. Below 850px, the conversation and artifact viewer stack vertically, controls remain reachable, and messages switch to a single-column layout.

## Accessibility

The composer uses a real textarea and submit button, assistant updates use `aria-live`, errors use `role=alert`, iframe content has a title, focus styles remain visible, and color is paired with text labels.
