# utils

Small helpers that other packages share.

- `color_utils.py`: `generate_color_from_string()` gives each pin type a stable color, made from
  a hash of the type name.

Log messages go through the standard `logging` module. Each module gets its logger with
`logging.getLogger(__name__)`. Set the `PYFLOWGRAPH_LOG_LEVEL` environment variable to `DEBUG`
to see the debug messages; the default level is `WARNING`.
