# PyFlowGraph Documentation

The [README](../README.md) is the user guide. [STATUS.md](../STATUS.md) tells what works, what
was checked and the known problems. [CONTRIBUTING.md](../CONTRIBUTING.md) tells how to set up,
run the tests and report a problem.

## Specifications

- [flow_spec.md](specifications/flow_spec.md): the Markdown graph format. The editor reads and
  writes this format.
- [flow_spec_llm.md](specifications/flow_spec_llm.md): a short version of the format for
  language models.
- [flow_spec_llm_generator.md](specifications/flow_spec_llm_generator.md): instructions for a
  language model that writes graph files.
- [ui-ux-specifications.md](specifications/ui-ux-specifications.md): the user interface design.

## Plans

These pages are plans. Some of the work is done, and the code can differ from them.

- [roadmap.md](roadmap.md): the planned features.
- [prd.md](prd.md): the product requirements.
- [workflow-automation-vision.md](workflow-automation-vision.md): the long-term direction.
- [competitive-analysis.md](competitive-analysis.md): other node editors.
- [priority-1-features-project-brief.md](specifications/priority-1-features-project-brief.md):
  the brief for the first features.
- [stories/3.4.epic.md](stories/3.4.epic.md) and
  [pin-type-visibility-enhancement.md](specifications/pin-type-visibility-enhancement.md): pin
  type badges and connection highlights. Not made yet.

## Design

- [technical_architecture.md](technical_architecture.md): the design of the command system,
  the groups and the single process execution. Written before the work.
- [architecture/coding-standards.md](architecture/coding-standards.md): code style.
- [architecture/tech-stack.md](architecture/tech-stack.md): the libraries and tools.

## Development

- [development/implementation-notes.md](development/implementation-notes.md): notes on the
  feature priorities.
- [development/modern-icons-guide.md](development/modern-icons-guide.md): the Font Awesome
  icons.
- [development/pyside6-testing-guide.md](development/pyside6-testing-guide.md): ways to test
  PySide6 code. To run the tests of this repository, follow
  [CONTRIBUTING.md](../CONTRIBUTING.md#run-the-tests).

## Bugs

[bugs/](bugs/) holds bug reports as Markdown files. The **Bug Sync** workflow copies them to
GitHub Issues when they change on `main`.
