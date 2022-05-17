#!/bin/bash
#
# Serve a jupyter lab environment from a compute node on Snellius
# see https://servicedesk.surfsara.nl/wiki/pages/viewpage.action?pageId=30660252
# usage: sbatch run_jupyter_on_compute_node.sh
 
# SLURM settings
#SBATCH -J jupyter_lab
#SBATCH -t 02:00:00
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH -p thin
#SBATCH --output=./slurm/slurm_%j.out
#SBATCH --error=./slurm/slurm_%j.out
 
# Use an appropriate conda environment
. ~/mamba/bin/activate stemmus

############ Use module MATLAB/2021a-upd3 to either run the source code or build the executable file ############
############ This needs a matlab license, make sure your account is added to the license pool ############
# Load matlab module
# On Snellius Try: "module spider MATLAB" to see how to load the module(s).
module load 2021
module load MATLAB/2021a-upd3

# Create executable file
mcc -m ./src/STEMMUS_SCOPE_exe.m -a ./src -d ./exe -o STEMMUS_SCOPE -R nodisplay -R singleCompThread
