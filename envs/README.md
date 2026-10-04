# Model environments

One environment per model, made by `bash scripts/setup_env.sh <name>`. The pipeline starts each model with the
interpreter named in `config/models.yaml` (`python: envs/<name>/bin/python`) and stops it before the next one,
so only one model is in memory at a time.

| Environment | Used by | Notes for the DGX Spark |
|---|---|---|
| `pipeline` | `drjev` itself | No GPU needed |
| `imajev` | imajev zero-shot, the untuned base model, all fine-tuned arms, imajev's trainer | Keep the server on its standard path (no `--fast`) until checked |
| `specialist` | The specialist classifier | PyTorch and torchvision from the CUDA 13 index |
| `neohorse` | NeoHorse Jev 4B | Its card records torch 2.8.0; a CUDA 13 build of torch is installed here instead |
| `jev_omni` | Jev-Omni | About 24 GB of weights |
| `visual_jev` | Visual-Jev 4B | Needs the Visual-Jev repository next to this folder |
| `glance` | Glance | Its library wants Python 3.11 |
| `jev27b` | JEV-27B-VL | 52 GB of weights; needs a CUDA 13 build of vLLM, which is the least certain install of all |

Each setup writes `envs/<name>.freeze.txt` with the exact package versions; keep these files with the results.

Nothing here has been run on a DGX Spark. Expect to adjust package versions; after each environment run
`drjev doctor` (does PyTorch see the GPU?) and `drjev check-model <run>` (does the model answer?).
