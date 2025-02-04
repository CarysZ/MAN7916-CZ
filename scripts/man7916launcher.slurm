#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=0-00:10:00
#SBATCH --error=results-%J.err
#SBATCH --output=results-%J.out
#SBATCH --job-name=MAN7916Setup
#SBATCH --gres=gpu:1

# load modules
module load python/python-3.11.4-oneapi-2023.1.0
source ~/MAN7916/.venv/bin/activate
python3 -m spacy download en_core_web_sm
python3 ./ml_asst_setup.py
