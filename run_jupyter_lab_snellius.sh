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
#SBATCH --output=./slurm_%j.out
#SBATCH --error=./slurm_%j.out

# Use an appropriate conda environment
. ~/mamba/bin/activate pystemmusscope

# Load module needed to run the model (no need for license)
module load 2021
### This is for Matlab Runtime
module load MCR/R2021a.3

### This is for Matlab
module load MATLAB/2021a-upd3

# Some security: stop script on error and undefined variables
set -euo pipefail

# Choose random port and print instructions to connect
PORT=`shuf -i 5000-5999 -n 1`
LOGIN_HOST_EXT=int4-pub.snellius.surf.nl
LOGIN_HOST_INT=int4

echo "Selected port is: " $PORT
echo
echo "To connect to the notebook type the following command from your local terminal:"
echo "ssh -L ${PORT}:localhost:${PORT} ${USER}@${LOGIN_HOST_EXT}"

ssh -o StrictHostKeyChecking=no -f -N -p 22 -R $PORT:localhost:$PORT $LOGIN_HOST_INT

# Start the jupyter lab session
jupyter lab --no-browser --port $PORT
