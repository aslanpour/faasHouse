#!/bin/bash

#delete leftovers
tmux kill-session -t mysession

# create a new tmux session
tmux new-session -d -s mysession

# create 4 rows
tmux split-window -v
tmux split-window -v
tmux split-window -v
tmux split-window -v

#split first row to 2 rows
tmux select-pane -t 0
tmux split-window -v

#now, there are 5 rows and 2 columns.
#select each row first pane, and split it in 2 columns

tmux select-pane -t 0
tmux split-window -h
# tmux resize-pane -y 5

tmux select-pane -t 2
tmux split-window -h
# tmux resize-pane -y 5

tmux select-pane -t 4
tmux split-window -h
# tmux resize-pane -y 5

tmux select-pane -t 6
tmux split-window -h
# tmux resize-pane -y 5

tmux select-pane -t 8
tmux split-window -h
# tmux resize-pane -y 5

#run commands in each pane


for i in {0..9}
do
  #select pane
  tmux select-pane -t $i
  #run ssh
  tmux send-key "ssh ubuntu@10.0.0.8$i" Enter
  

  #if no argument passed, kill hedgi and re-run it, monitor it
  if [ "$#" -eq 0 ]; then
  	#kill hedgi
  	tmux send-key "kill -9 \$(ps -aux |grep hedgi | awk '{print \$2}')" Enter
        #run hedgi
  	tmux send-key "python3 hedgi.py" Enter

  #else if arguemtn is passed and it is tail, observe logs
  else
	tmux send-key "tail -F /home/ubuntu/logs/hedgi.log" Enter
  fi
done



# attach to the new session
tmux attach-session -t mysession


#to close
#tmux kill-session -t mysession

