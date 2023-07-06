#!/bin/bash
#settings
log_folder="/home/ubuntu/logs/"
homo1_alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1
test_name_format="alg-ALGORITHM_oth1-SCHEDCONF_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-WORKLOAD_RATE_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-OTHERSCONFS_round-ROUND"
NODES=("homo1" "homo2" "homo3" "homo4" "homo5" "homo6" "homo7" "homo8" "homo9" "homo10")
# NODES=("homo1")
NODES_IP=("10.0.0.80" "10.0.0.81" "10.0.0.82" "10.0.0.83" "10.0.0.84" "10.0.0.85" "10.0.0.86" "10.0.0.87" "10.0.0.88" "10.0.0.89" )
# NODES_IP=("10.0.0.80")
user_name="ubuntu"
ALGORITHMS=("greedy" ) # idle local default random greedy shortfaas binpacking
SCHEDCONFS=("z1006030-stick0.2") # na plug1000000 plug1005000 plug1003000 plug1007000 z1006030-stick0.2 z1006030-stick0.8 plug1005030 plug1007030 plug1002000
OTHERSCONFS=("boot5-rep1-hicup2block30") # na boot5-rep1-hicup3block20  boot5-rep1-hicup2block30

ROUNDS=( "1"  ) # ( "2" "3")
WORKLOAD_RATES=("13") # 33 13 14 31
exclude_hedgi_log=true

#RUN

#per node (get index of node by !)
for i in "${!NODES[@]}"; do
    test_name=""
    
    #mkdir for logs if not exists
    if [ ! -d "${log_folder}${NODES[$i]}" ]; then
        mkdir -p "${log_folder}${NODES[$i]}"
    fi
    
    #per algorithm
    #make path for the remote server
    for algorithm in "${ALGORITHMS[@]}"; do
        for workload_rate in "${WORKLOAD_RATES[@]}"; do
            #per round
            for round in "${ROUNDS[@]}"; do
                #per schedconf
                for schedconf in "${SCHEDCONFS[@]}"; do
                    #per othersconf
                    for othersconf in "${OTHERSCONFS[@]}"; do
                        #get a fresh test_name_format and work on it as follows.
                        echo "*************** ${algorithm}"
                        #replace algorithm
                        test_name=${test_name_format/"ALGORITHM"/"$algorithm"}
                        #replace workload_rate
                        test_name=${test_name/"WORKLOAD_RATE"/"$workload_rate"}
                        #replace round
                        test_name=${test_name/"ROUND"/"$round"}    
                        #replace schedconf
                        test_name=${test_name/"SCHEDCONF"/"$schedconf"}
                        #replace others conf
                        test_name=${test_name/"OTHERSCONFS"/"$othersconf"}

                        echo "test_name ${test_name}"
                        #copy dir from remote to master
                    
                        #copy all files of the dir
                        source="${user_name}@${NODES_IP[$i]}:${log_folder}${NODES[$i]}_${test_name}"
                        dest="${log_folder}${NODES[$i]}"
                        echo "${source}      -------  ${dest}"

                        #all file or exclude hedgi.log
                        if [ "$exclude_hedgi_log" = true ]; then    
                            #copy all files except hedgi.log
                            rsync -avr -e "ssh -l ${user_name}" --exclude 'hedgi.log' "${source}" "${dest}" && echo "****node=${NODES[$i]} ***algorithm=${algorithm}***round=${round}****************   Ok" || "$NODES[$i] ******************************  No such file!!!!!!!}"
                        else
                            scp -r "${source}" "${dest}" && echo "****node=${NODES[$i]} ***algorithm=${algorithm}***round=${round}****************   Ok" || "$NODES[$i] ******************************  No such file}"
                        fi
                    done #OTHERSCONFS
                done #SCHEDCONFS
            done #ROUNDS
        done #WORKLOAD_RATES
    done #ALGORITHMS

        
    #add metrics to metrics.xlsx and metrics.csv files
    # metrics_json="${dest}/${nodes[$i,1]}_${test_name}/metrics.txt"
    # echo "metrics_json=${metrics_json}"
    # source ./bmetricsadd.sh "${metrics_json}"

done
















