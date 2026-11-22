#!/usr/bin/env bash
set -eu
code_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ ${1:-} == --help || ${1:-} == -h || $# == 0 ]]; then
    echo "VLA_WORKDIR=/path/to/prepared/stand bash run.sh {prepare|train|eval}"
    echo "The stand contains dart/.venv, simenv, libero-config, checkpoints/pi05_libero and data/libero_90."
    exit 0
fi
cd "${VLA_WORKDIR:-$code_dir}"
work="$(pwd -P)"
export OPENPI_DATA_HOME="$work/cache" LIBERO_CONFIG_PATH="$work/libero-config"
export PYTHONPATH="$work/dart:$work/dart/src:$work/dart/packages/openpi-client/src:$work/dart/third_party/libero-view${PYTHONPATH:+:$PYTHONPATH}"
export MUJOCO_GL=egl PYOPENGL_PLATFORM=egl MUJOCO_EGL_DEVICE_ID=0
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export XLA_PYTHON_CLIENT_PREALLOCATE=false HF_HOME="$work/cache/hf"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false
export JAX_COMPILATION_CACHE_DIR="$work/cache/jax"
if [[ $1 == train ]]; then
    export XLA_PYTHON_CLIENT_ALLOCATOR=platform
    unset XLA_CLIENT_MEM_FRACTION XLA_PYTHON_CLIENT_MEM_FRACTION
fi
exec "$work/dart/.venv/bin/python" -u "$code_dir/experiment.py" "$@"
