# PyFlowGraph Examples

Each file here is a graph in the format that
[docs/specifications/flow_spec.md](../docs/specifications/flow_spec.md) describes. The editor
trusts these files, so it opens them without the **Run Code from This Graph?** question.

## Open an Example

1. Click **File > Load Graph...**.
2. Select a file in this folder.
3. Press `F5` to run the graph. The results show in the nodes and in the **Output Log**.

## Files

| File | What it does | Needs |
| --- | --- | --- |
| `password_generator_tool_group.md` | Makes a password from the chosen character sets and scores its strength. Two nodes are in a group. | Python only |
| `recipe_nutrition_calculator.md` | Reads a list of ingredients, looks up the nutrition values and writes a report. | Python only |
| `weather_data_processor.md` | Makes simulated weather data, then reports statistics and trends. | Python only |
| `nvidia_gpu_computer_vision_pipeline.md` | Loads `sample_images/cat.jpg` and processes it with PyTorch tensors. It uses the GPU when CUDA is available. | A graph environment with `torch`, `torchvision`, `Pillow` and `numpy` |

The editor opens `password_generator_tool_group.md` at the first start.

## Set Up the PyTorch Example

1. Open `nvidia_gpu_computer_vision_pipeline.md`.
2. Click **Environment > Manage Environment...**.
3. Check the list of packages.
4. Click **Create / Update Environment** and wait until pip finishes.
5. Press `F5`.
