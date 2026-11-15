# Security

Report a security problem privately. On the **Security** tab of the repository, click
**Report a vulnerability**. Do not open a public issue, and do not put the details of the problem
in one. If the button is not there, open an issue that asks for a private contact, with no
details.

A graph file is a program. The editor runs the **GUI Definition** and **GUI State Handler** code
of each node when it opens or pastes a graph, and the other node code when you run the graph.
This code can do what the editor can do. Open only graphs that you trust. This is how the program
works, and is not a security problem by itself.

Before the editor runs the code of a graph that you have not trusted, it asks. It trusts the
bundled examples, the files that you save and the file versions that you accepted before. At
startup it reopens the last graph only if the graph is trusted. It refuses graph dependencies
that pip would read as options.

Examples of useful reports:

- A way to open, reopen or paste an untrusted graph that runs its code without the question.
- A graph dependency entry that gets past the pip option check and makes pip use another
  package index, a local file or other options.
- A graph file that runs code that is not in one of its code blocks, for example from its
  metadata, a node title, a group or a connection.
- A graph that installs packages, or runs code from a virtual environment, that the user did not
  select.
- The editor sending graph data or other data off the computer.
- Text in the repository, for example a document or a template, that makes the AI agent of a
  contributor run commands or send data.

Remove credentials, private paths and files that you cannot share from logs and samples.
