## Binary Diffing and Marimo Rust

Marimo notebook to compare and search the binary diffing results using the Rust Diff Plugin for Binary Ninja https://github.com/meerkatone/rust_diff

## Clone the repo
git clone https://github.com/meerkatone/rust_diff.git

## Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

## Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

## Setup venv and Marimo
uv venv --python 3.13

source .venv/bin/activate

cd Binary-Diffing-and-Marimo-Rust

uv pip install marimo

## Launch the notebook
marimo edit ./binary_ninja_diffing_rust

The notebook will ask you to install the required dependencies via uv.
