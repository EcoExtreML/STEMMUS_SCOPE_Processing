#!/bin/bash
#
# Serve a jupyter lab environment from a compute node on Snellius
# see https://servicedesk.surfsara.nl/wiki/pages/viewpage.action?pageId=30660252
# usage: sbatch run_jupyter_lab_snellius_dev.sh
 
# SLURM settings
#SBATCH -J jupyter_lab
#SBATCH -t 02:00:00
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH -p thin
#SBATCH --output=./slurm/slurm_%j.out
#SBATCH --error=./slurm/slurm_%j.out
 
 # Some security: stop script on error and undefined variables
set -euo pipefail

# Use an appropriate conda environment
. ~/mamba/bin/activate stemmus

############ Use module MATLAB/2021a-upd3 to either run the source code or build the executable file ############
############ This needs a matlab license, make sure your account is added to the license pool ############
# Load matlab module
# On Snellius Try: "module spider MATLAB" to see how to load the module(s).
module load 2021
module load MATLAB/2021a-upd3

# Choose random port and print instructions to connect
PORT=`shuf -i 5000-5999 -n 1`
LOGIN_HOST_EXT=int3-pub.snellius.surf.nl
LOGIN_HOST_INT=int3
 
echo "Selected port is: " $PORT
echo
echo "To connect to the notebook type the following command from your local terminal:"
echo "ssh -L ${PORT}:localhost:${PORT} ${USER}@${LOGIN_HOST_EXT}"
 
ssh -o StrictHostKeyChecking=no -f -N -p 22 -R $PORT:localhost:$PORT $LOGIN_HOST_INT
 
# Start the jupyter lab session
jupyter lab --no-browser --port $PORT
