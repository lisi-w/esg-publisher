#!/bin/bash

bash /export/witham3/esgf/conda.sh
. ~/.bashrc
conda activate replica-pub
cd /export/witham3/pub-internal
running=`ps -fe | grep pub-workflow | wc -l`
if [ $running -gt 1 ]
then
  exit 0
else
  thedate=`date +%y%m%d_%H%M` ; time nohup python3 pub-workflow.py > /esg/log/publisher/main/replica-pub.$thedate.log
fi
