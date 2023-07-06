#echo "epoch=0" >  /home/ubuntu/logs/config.txt

#warm scheduling for greedy (already has), random, bin-packing, shortfass???
#kubernetes, every round, give it only up nodes, instead of all nodes
import getpass

#epoch driver
# To stop hedgi from auto-start at boot, set "test_name = []"" or "sudo systemctl disable hedgi.service"
test_name = [

    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    
                                     ]


# test_name=[]

"""
boot=bootup_delay
rep=repetition
locimag=Use-Local-Image header
actrate4dur5seed1=avtive_sensor interarrival_rate, event_duration, seed_start
m5 m15 m20 = min_battery_charge_warmup_percent default was 10
"""
"""
'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',

'alg-ccgrid_oth1-warm-no-z1006030-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
'alg-ccgrid_oth1-warm-y-z1006030-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',            
'alg-ccgrid_oth1-warm-no-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
'alg-ccgrid_oth1-warm-no-z1008020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
'alg-ccgrid_oth1-warm-no-z1005040-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
'alg-ccgrid_oth1-warm-y-z1009015-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',

'alg-binpacking_oth1-warm-no_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
'alg-binpacking_oth1-warm-y_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
#assignments
    'alg-shortfaas_oth1-plug1000000_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
    'alg-shortfaas_oth1-plug1006000_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006020_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
    'alg-shortfaas_oth1-plug1006020-warm-y_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006060_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-hospital_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
    'alg-mthg_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-2',
    'alg-ffd_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-optimal_oth1-p1006040-ren1.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
#scheduling intervals
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
#battery size
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1000_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1000_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1000_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1500_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1500_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1500_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1750_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1750_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1750_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1750_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1750_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
#cpu governor
'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1000_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1500_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-power_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-power_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-power_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-power_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',

    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-perform_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-perform_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-perform_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-perform_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
#workload 75%
'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate4dur5seed0-testdur180_round-1',
#workload 50%
'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate8dur5seed0-testdur180_round-1',
#workload 25%
'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate12dur5seed0-testdur180_round-1',
    
    
#async
'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1.5_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-3',

    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-async_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
#local
'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-3_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-10_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-30_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1000_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1500_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-power_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-conserv_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ppowerschint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-perform_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur0seed0-testdur180_round-1',
#solar size
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
#solar
'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-0.8_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.2_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-1800_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1.4_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
#no cpu limit
'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-shortfaas_oth1-plug1006040_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-default_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-random_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-ccgrid_oth1-warm-y-z1007020-st0.2_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-1',
    'alg-local_oth1-na_scale-hpa_repamax-1_cpureq-1800_cpulim-3600_oth2-na_workloadtyp-sync_shp-off_rng-13-arrival1_oth3-hold1_cpugov-ondemand_schint-5_battsize-1250_solarsize-1_oth4-boot5-rep1-actrate0dur5seed0-testdur180_round-2',

    #############


"""

#alg-XXX_oth1-XXX_scale-XXX_repamax-XXX_cpureq-XXX_cpulim-XXX_oth2-XXX_workloadtyp-XXX_shp-XXX_rng-XXX_oth3-XXX_cpugov-XXX_schint-XXX_battsize-XXX_solarsize-XXX_oth4-XXX_round-XXX


variable_parameters=['workload_cfg', 'scheduler_name', 'plugins', 'stickiness', 'warm_scheduler', 'solar_panel_scale', 'max_battery_charge', 'scheduling_interval', 'cpu_governor', 'interarrival_rate']

test_duration= 180* 60 ##### seconds
# test_duration= 120* 60 ##### seconds
#[0] position (e.g.,COORDINATOR, PEER, or -) [1] node (host) name [2] node ip
#for scheduling, max 5 nodes are considered.
nodes=[["COORDINATOR","master","10.0.0.90"],
       ["PEER", "homo1","10.0.0.80", "ubuntu"],
       ["PEER", "homo2","10.0.0.81", "ubuntu"],
       ["PEER", "homo3","10.0.0.82", "ubuntu"],
       ["PEER", "homo4","10.0.0.83", "ubuntu"],
       ["PEER", "homo5","10.0.0.84", "ubuntu"],
       ["PEER", "homo6","10.0.0.85", "ubuntu"],
       ["PEER", "homo7","10.0.0.86", "ubuntu"],
       ["PEER", "homo8","10.0.0.87", "ubuntu"],
       ["PEER", "homo9","10.0.0.88", "ubuntu"],
       ["PEER", "homo10","10.0.0.89", "ubuntu"],]

accelerators = {nodes[0][1]: [], nodes[1][1]: [], nodes[2][1]: [], nodes[3][1]: [], nodes[4][1]: [], nodes[5][1]: [], nodes[6][1]: [], nodes[7][1]: [], nodes[8][1]: [], nodes[9][1]: [],nodes[10][1]: [],}
# accelerators = {'w1': [], 'w2': [], 'w3': [], 'w4': ['tpu'], 'w5': ['gpu'], 'w6': [], 'w7': []}

#load balancing

#if only 1 node
# backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''},]

#if linkerd
# backends = [{'service': node[1] + '-' + 'ssd', 'weight': 1000} for node in nodes if node[0] == 'PEER']
#if envoy
#even (and also used for least-request, lease-request-p2c, and least-request-local-executor)
backends = [ {'service': nodes[1][1] + '-ssd','weight': 200, 'ip': '', 'port': ''},
             {'service': nodes[2][1] + '-ssd','weight': 200, 'ip': '', 'port': ''},  {'service': nodes[3][1] + '-ssd','weight': 200, 'ip': '', 'port': ''}, 
             {'service': nodes[4][1] + '-ssd','weight': 200, 'ip': '', 'port': ''}, {'service': nodes[5][1] + '-ssd','weight': 200, 'ip': '', 'port': ''},
             {'service': nodes[6][1] + '-ssd','weight': 200, 'ip': '', 'port': ''}, {'service': nodes[7][1] + '-ssd','weight': 200, 'ip': '', 'port': ''},
             {'service': nodes[8][1] + '-ssd','weight': 200, 'ip': '', 'port': ''}, {'service': nodes[9][1] + '-ssd','weight': 200, 'ip': '', 'port': ''},
             {'service': nodes[10][1] + '-ssd','weight': 200, 'ip': '', 'port': ''}]
# #static energy-totall
# backends = [{'service':'w2-ssd','weight': 192, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 186, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 130, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 219, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 273, 'ip': '', 'port': ''}]
#static cpu * frequency
# backends = [{'service':'w2-ssd','weight': 206, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 200, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 375, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 102, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 118, 'ip': '', 'port': ''}]
#static AI confidence
# backends = [{'service':'w2-ssd','weight': 193, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 193, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 188, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 233, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 193, 'ip': '', 'port': ''}]
#static QoS response time (exec time or tail latency?)
# backends = [{'service':'w2-ssd','weight': 170, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 213, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 378, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 128, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 111, 'ip': '', 'port': ''}]
#static throughput
# backends = [{'service':'w2-ssd','weight': 245, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 273, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 265, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 100, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 117, 'ip': '', 'port': ''}]
#static energy-processing
# backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 124, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 499, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 93, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 85, 'ip': '', 'port': ''}]

#static cost
# backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 212, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 355, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 82, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 151, 'ip': '', 'port': ''}]

#static ai-precision
# backends = [{'service':'w2-ssd','weight': 202, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 202, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 136, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 258, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 202, 'ip': '', 'port': ''}]

#static throughput-updated (used also for weighted least request algorithm)
# backends = [{'service':'w2-ssd','weight': 158, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 184, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 444, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 114, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 99, 'ip': '', 'port': ''}]

#static throughput-optimal (weights are measured based on optimal observations of least connection policy)
# backends = [{'service':'w2-ssd','weight': 116, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 146, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 319, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 348, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 70, 'ip': '', 'port': ''}]

#To switch from envoy to openfaas, it is enough to only change handler to openfaas-gateway and vice versa
#For type, 'handler' = openfaas-gateway, linkerd or envoy.
#For type, if 'handler'=linkerd, service_mesh paramter must be True.
#For type['control-plane], vlue can be centralized, distributed or decentralized.
#For algorithm, if ['type']['handler'] == 'linkerd, then algorithm = even or static
#For algorithm, if ['type']['handler'] == 'envoy, algorithm = local or (even or static). If local, postfix = 'func_name' else postfix = ''
#For frontend if envoy, if 'static' , 'frontends': [{'type': 'static', 'listeners': {'name': 'envoy', 'ip': '10.43.10.10', 'address': '0.0.0.0', 'port': 9000, 'route_by': 'path', 'match': {'prefix': '/'}, 'path': '/', 'postfix': '', 'cluster': 'cluster1', 'redis_server_ip': '10.43.189.161'}}],
#For frontends, if openfaas-gateway, 'frontends': [{'type': 'static', 'listeners': {'name': 'openfaas-gateway', 'ip': '10.0.0.90', 'port': '31112', 'path': '/async-function/', 'postfix': 'func_name', 'redis_server_ip': '10.43.189.161'},},],
#For frontends, if name == openfaas-gateway, path can be '/function/' or  '/async-function/' for sync and async. Only async returns callback
#For frontends, if type 'dynamic', listeners['ip'] must be measured on runtime to be given to workload_generator
#For object_storage 1,  default --> {'read':{'decoupled': False, 'type':'anything', 'ip': 'anything', 'port': 5000}},
#For object_storage 2,  decoupled local-generator --> {'read':{'decoupled': True, 'type':'decentralized-tinyobj', 'ip': 'local-generator', 'port': 5500}},
#For object_storage 2,  decoupled local-executor --> {'read':{'decoupled': True, 'type':'decentralized-tinyobj', 'ip': 'local-executor', 'port': 5500}},
#For object_storage 3, decoupled centralized --> {'read':{'decoupled': True, 'type':'centralized-tinyobj', 'ip': '10.0.0.91', 'port': 5500}},
#For object_storage, minio centralized --> {'read': {'decoupled': True, 'type':'centralized-minio', 'ip': '10.0.0.96', 'port': 9000, 'resource': '/', 'bucket': 'mybucket', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
#For object_storage, minio decentralized -->  'object_storage': {'read': {'decoupled': True, 'type':'decentralized-minio', 'ip': 'local-generator', 'port': 9000, 'resource': '/', 'bucket': 'mybucket130k', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
#For object_storage, minio --> wget https://dl.minio.io/server/minio/release/linux-arm/minio
#wget https://dl.minio.io/client/mc/release/linux-arm/mc
#sudo ln -s /home/ubuntu/minio /usr/bin/minio
#sudo ln -s /home/ubuntu/mc /usr/bin/mc
#wget https://dl.min.io/server/minio/release/linux-arm64/minio & chmod +x minio & mkdir -p /data & minio server /home/ubuntu/data &
#open dashboard 10.0.0.91:9000, create bucket 'mybucket', set public access to bucket
#populate mybucket using minio-put.py
#For object_storage, if port different than main flask, a tineobj.py my be ran on hosts listening on the port.
#For add_headers, {'Use-Local-Image': '0-170'}, or {'Internal-Connection': 'close'}, or {'Internal-Session': 'anything'},
#Do not use object_storage read with add_headers['Use-Local-Image'] 
#For backend_discovery, value = static (use 'backends') or dynamic.
#For backend_discovery, if type['handler'] == linkerd, then 'type' = 'static' and deployments['backends']['TrafficSplit'] and ['Function'] name must be equal.
#For 'deploy', if ['type']['handler'] == envoy and ['type']['deployment'] == kubernetes, then 'deploy'= ['Deployment-envoy', 'Service-envoy',] and Requires envoy.yaml file address. 
#For 'deployments'['Deployment-envoy'] if 'nodeName' != master and ARM, envoy image will fail and instead use image: thegrandpkizzle/envoy:1.24.0 but for AMD value of 'host_user_ip' is like 'ubuntu@10.0.0.91'
#For 'deploy', if ['type']['handler'] == linkerd  and ['type']['deployment'] == kubernetes, then 'deploy'= ['Function-function']. 
#For envoy, two types of lb_policy, "round_robin" (default) or "LEAST_REQUEST". 
#For envoy, If lb_policy is "LEAST_REQUEST", least_request_lb_config" is applied to "cluster", defined in 'backend' key, but be careful about "load_balancing_weight" that may interfere.
#If purely LEAST_REQUEST is desired, wieghts of backends must be equal; otherwise, it acts as "weighted least request".
#active_request_bias is not taking affect now
#'choice_count': len(backends) or 2. If power of 2 choices is desired, value is 2
load_balancing ={
        'type': {'adaptive': False, 'control-plane': 'centralized', 'handler': 'openfaas-gateway', 'deployment': 'kubernetes'}, 
        'interval': 800,
        'algorithm': 'static',
        'lb_policy': 'LEAST_REQUEST',
        'accelerators': accelerators,
        'admin':{'name': 'admin', 'ip': '10.0.0.90', 'port': 8000,},
        'frontends': [{'type': 'static', 'listeners': {'name': 'openfaas-gateway', 'ip': '10.0.0.90', 'port': '31112', 'path': '/function/', 'postfix': 'func_name', 'redis_server_ip': '10.43.189.161'},},],
        'object_storage': {'read': {'decoupled': True, 'type':'decentralized-minio', 'ip': 'local-executor', 'port': 9000, 'resource': '/', 'bucket': 'mybucket130k', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
        'add_headers':{},
        'backend': {'choice_count': len(backends), 'active_request_bias': 1.0},
        'backend_discovery': {'type': 'static', 'backends': backends},
        'deploy': ['Deployment'],
        'deployments': {
            'Deployment-envoy': 
                {'api_version': 'apps/v1', 'kind': 'Deployment', 'object_name': 'envoy', 'namespace': 'openfaas-fn', 
                'image': 'envoyproxy/envoy:v1.24.0', 'nodeName': 'master', 'host_user_ip': 'ubuntu@10.0.0.91', 'annotations': {'version': '1'}, 'ports': [{'containerPort': 9000}], 
                'volumeMounts': [{'name': 'envoy-config', 'mountPath': '/etc/envoy/envoy.yaml'},],
                'volumes': [{'name': 'envoy-config', 'hostPath': {'path': '/home/ubuntu/envoy.yaml'}},], 'manifest': {}, 'envoy-config': {}},
            'Service-envoy':
                {'api_version': 'v1', 'kind': 'Service', 'object_name': 'envoy', 'namespace': 'openfaas-fn', 'clusterIP': '10.43.10.10',
                'ports': [{'protocol': 'TCP', 'port': 9000, 'targetPort': 9000}], 'manifest': {},},
            'Function-linkerd':
                {'api_version': 'openfaas.com/v1', 'kind': 'Function', 'object_name': 'gw-func', 'namespace': 'openfaas-fn', 'image': 'aslanpour/ssd:cpu-tpu-amd64',
                'labels': {'com.openfaas.scale.min': '1','com.openfaas.scale.max': '1'}, 'annotations': {'linkerd.io/inject': 'enabled'},
                'constraints': ['kubernetes.io/hostname=master'], 'manifest': {},},
            'TrafficSplit':
                {'api_version': 'split.smi-spec.io/v1alpha2', 'kind': 'TrafficSplit', 'object_name': 'my-traffic-split','namespace': 'openfaas-fn',
                'service': 'gw-func', 'operation': 'safe-patch','manifest': {}, 'backends': [],},
        }
    
    } #variable

#NOTE if True, queues must be already created! and follows the name pattern as queue-worker-functionName. Only works in async.
multiple_queue=False
#if true, Linkerd is required for OpenFaaS
service_mesh=True

#cpu intensity
model_inference_repeat = 1

redis_server_ip= "10.43.189.161" #assume default port is selected as 3679

#local #default-kubernetes #random #bin-packing #greedy (is CCGRID) #shortfaas #hospital_resident #mthg #ffd
scheduler_name = [ "shortfaas", "shortfaas", "default", "default","random", "random","greedy", "greedy","local", "local", "shortfaas","default", "default","random", "greedy","local",] #variable

scheduling_interval= [5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60, 5 * 60] #variable  ### second -- default 5 *  60 equivalent to 30 min
#(greedy only) zonal categorization by Soc %
#[0] zone [1] priority [2] max Soc threshold [3] min Soc threshold
#1006030
zones = [["rich", 1, 100, 70],
        ["vulnerable", 3, 70, 20],
        ["poor", 2, 20, 10],
        ["dead", 4, 10, -1]] #-1 means 0
#if 1250=100%, then 937.5=75%, 312.5=25% and 125=10%


#plugins and weights for shortfaas scoring
plugins = [{'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40},
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, 
           {'energy':100, 'locally':60, 'sticky':40}, ] #variable

#==0 only if scheduler_name=="greedy" and warm_scheduler=True
#and should be limited just in case function is not locally placed. (not implemented yet this part), so it is applied all the time if used
#this time takes for newly up node to be ready to send_sensors
boot_up_delay = 5 * 60   ####
#(greedy only) scheduler_greedy_config
sticky = True # it requires offloading=True to be effective
#(greedy only) 
stickiness = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2 , 0.2] #variable #20% # it requires offloading=True to be effective #####
#(greedy only) 
warm_scheduler = [False, False, False, False, False, False, True, True, False, False, False, False, False, False, False, False] # it requires offloading=True to be effective -- if true, workload will be generated and sent once the node is down.
hospital_and_mthg_placment_capacity = 2
#re-placement strategy: 
#To keep everything as default, put only None,or {} or 0 or ""
# default type is RollingUpdate in Kubernetes. Otherwise, set to 'Recreate' but remove the key 'rollingUpdate'.
#If type = rollingUpdate, the key rollingUpdate has maxSurge (kubernetes default=25%, openfaas default=1) and maxUnavailable (kubernetes default=25%, openfaas default=0) to set. 
#If maxUnavailable=0, only a pod is removed if a new one is already ready. This causes resource insufficient error if the new pod + old pod can not be up at the same time on the node.
replacement_strategy = {'type': 'RollingUpdate',
                        'rollingUpdate':
                            {
                                'maxSurge': 1,
                                'maxUnavailable': 1
                            }}

#cpu frequency: governors: ondemand, powersave, performance, conservative
#set_frequencies for setting static frequencies is used only if governors is 'userspace'.
#'jetson_nano_nvp_mode': 'max-10w' or '5w'
#key "governors" tells which governor must be used.
#sample min frequency: 600000
cpu_freq_config={"effect": ["LOAD_GENERATOR", "STANDALONE"],"governors": "IS_SET_BY_cpu_governor_variable",
    "set_min_frequencies": 0, "set_max_frequencies": 0, "set_frequencies": 600000, 'jetson_nano_nvp_mode': 'max-10w'}

cpu_governor = ['ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand', 'ondemand'] #variable
#??????????????????image name has gpu
apps = {"ssd": True, "yolo3": False, "irrigation":False, "crop-monitor": False, "short": False}
#w5-ssd is just for Nano to pull gpu-based image.??
apps_image = {"ssd": "aslanpour/ssd:cpu-tpu", "w5-ssd": "aslanpour/ssd:cpu-tpu-gpu", "yolo3": "aslanpour/yolo3-quick", "irrigation":"aslanpour/irrigation", "crop-monitor": "aslanpour/crop-monitor", "short": "aslanpour/short"}

#[WORKLOAD]
#"sync" or "async-static" or "async-poisson" (concurrently) or "async-exponential" (interval) or "exponential-poisson"
#if async, a callback header is set in request that will be called by queue-worker of openfaas if request is sent on /async-funciton/
workload_type ="sync"

#No workload test: set workload_type ="sync" and concurrency=0
worker = "thread"  # or "gevent": low CPU usage (~5% improvement) but slower admission (0.098s vs 0.1s) and super difference between the max values.
seed = 5
session_enabled = True #if false, workload generator issues a new HTTP connection per request. On a Pi 3, sessions improve admission time by 25%, CPU usage 8% and memory 2% than new HTTP connection per request on Pi 3.

#Stages - Note: if max concurrently is more than 10 times the original concurrently, adjust the max_pool for requests.session.
shape_OFF = [{"stageStartTimePercent":None, "stageEndTimePercent": None, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": None,"stageSlope": None, "stageStepLength": None},]
shape_RampUp5 = [{"stageStartTimePercent":None, "stageEndTimePercent": None, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": 3,"stageSlope": None, "stageStepLength": None},]
shape_HalfRampUp5Down = [{"stageStartTimePercent":None, "stageEndTimePercent": 50, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": 3,"stageSlope": None, "stageStepLength": None},
                        {"stageStartTimePercent":50.01, "stageEndTimePercent": None, "stageConcurrentlyStart": 5, "stageConcurrentlyEnd": None,"stageSlope": None, "stageStepLength": None},]

shapes = {nodes[0][1]:shape_OFF, nodes[1][1]:shape_OFF, nodes[2][1]:shape_OFF, nodes[3][1]:shape_OFF, nodes[4][1]: shape_OFF, nodes[5][1]: shape_OFF, nodes[6][1]: shape_OFF, nodes[7][1]: shape_OFF, nodes[8][1]: shape_OFF, nodes[9][1]: shape_OFF, nodes[10][1]: shape_OFF}

#[0]: ssd, [1]: yolo3, [2]: irrigation, [3]: crop-monitor, [4]: short
#[x][0] iteration [x][1]interval/exponential lambda (lambda~=avg)
#[x][2]concurrently/poisson lambda (lambda~=avg) [x][3] random seed (def=5)]. In async means x requests (in x threads) per y sec. In sync means x spawners (in threads) sending 1 req each back to back.
# [x][4] shape, [x][5] worker "thread" or "gevent"
#in the main.py is w_config = my_app[3] --> w_config[0-3]
#if static, only set int values ????? otherwise, workload() gives error.

#1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7,8,8,8,8,8,9,9,9,9,9,10,10,10,10,10,
workload_cfg ={
nodes[0][1]:[[15000, 1, [0,0,0,0],seed, shapes[nodes[0][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[0][1]],worker], [10000, 10, 1,seed, shapes[nodes[0][1]],worker], [10000, 1, 1,seed, shapes[nodes[0][1]],worker], [10000, 1, 1,seed, shapes[nodes[0][1]],worker]],
nodes[1][1]:[[15000, 1, [1,1,1,1,1,1,1,1,1,1,1,1,1,1,],seed, shapes[nodes[1][1]],worker], [10000, 20, 1.9,seed, shapes[nodes[1][1]],worker], [10000, 15, 1.0,seed, shapes[nodes[1][1]],worker], [10000, 1, 1,seed, shapes[nodes[1][1]],worker], [10000, 1, 1,seed, shapes[nodes[1][1]],worker]],
nodes[2][1]:[[15000, 1, [2,2,2,2,2,2,2,2,2,2,2,2,2,2,],seed, shapes[nodes[2][1]],worker], [10000, 10, 1.9,seed, shapes[nodes[2][1]],worker], [10000, 8, 1.0,seed, shapes[nodes[2][1]],worker], [10000, 10, 1,seed, shapes[nodes[2][1]],worker], [10000, 10, 1,seed, shapes[nodes[2][1]],worker]],
nodes[3][1]:[[15000, 1, [3,3,3,3,3,3,3,3,3,3,3,3,3,3,],seed, shapes[nodes[3][1]],worker], [10000, 10, 1.9,seed, shapes[nodes[3][1]],worker], [10000, 8, 1.0,seed, shapes[nodes[3][1]],worker], [10000, 10, 1,seed, shapes[nodes[3][1]],worker], [10000, 10, 1,seed, shapes[nodes[3][1]],worker]],
nodes[4][1]:[[15000, 1, [1,1,1,1,1,1,1,1,1,1,1,1,1,1,],seed, shapes[nodes[4][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[4][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[4][1]],worker], [10000, 10, 1,seed, shapes[nodes[4][1]],worker], [10000, 10, 1,seed, shapes[nodes[4][1]],worker]],
nodes[5][1]:[[15000, 1, [2,2,2,2,2,2,2,2,2,2,2,2,2,2,],seed, shapes[nodes[5][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[5][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[5][1]],worker], [10000, 10, 1,seed, shapes[nodes[5][1]],worker], [10000, 10, 1,seed, shapes[nodes[5][1]],worker]],
nodes[6][1]:[[15000, 1, [3,3,3,3,3,3,3,3,3,3,3,3,3,3,],seed, shapes[nodes[6][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[6][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[6][1]],worker], [10000, 10, 1,seed, shapes[nodes[6][1]],worker], [10000, 10, 1,seed, shapes[nodes[6][1]],worker]],
nodes[7][1]:[[15000, 1, [1,1,1,1,1,1,1,1,1,1,1,1,1,1,],seed, shapes[nodes[7][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[7][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[7][1]],worker], [10000, 10, 1,seed, shapes[nodes[7][1]],worker], [10000, 10, 1,seed, shapes[nodes[7][1]],worker]],
nodes[8][1]:[[15000, 1, [2,2,2,2,2,2,2,2,2,2,2,2,2,2,],seed, shapes[nodes[8][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[8][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[8][1]],worker], [10000, 10, 1,seed, shapes[nodes[8][1]],worker], [10000, 10, 1,seed, shapes[nodes[8][1]],worker]],
nodes[9][1]:[[15000, 1, [3,3,3,3,3,3,3,3,3,3,3,3,3,3,],seed, shapes[nodes[9][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[9][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[9][1]],worker], [10000, 10, 1,seed, shapes[nodes[9][1]],worker], [10000, 10, 1,seed, shapes[nodes[9][1]],worker]],
nodes[10][1]:[[15000, 1,[1,1,1,1,1,1,1,1,1,1,1,1,1,1,],seed, shapes[nodes[10][1]],worker], [10000, 6, 1.9,seed, shapes[nodes[10][1]],worker], [10000, 5, 1.0,seed, shapes[nodes[10][1]],worker], [10000, 10, 1,seed, shapes[nodes[10][1]],worker], [10000, 10, 1,seed, shapes[nodes[10][1]],worker]],}

#sensor itself drops for environmental rerasons for examples, if hiccup_times=0, no hiccups
hiccup_times = 0
hiccup_duration = 30 * 60
hiccup_starts = {"homo1":[1,6,9], "homo2":[8,1,4,], "homo3":[5,8,1], "homo4":[4,7,10], "homo5":[9,2,5], "homo6":[7,10,3], "homo7":[2,5,8], "homo8":[10,3,6], "homo9":[1,4,7], "homo10":[6,9,2]}
hiccups_injection={nodes[0][1]: [],
                    nodes[1][1]:[{"start": hiccup_starts["homo1"][i] / 10 * test_duration, "end": hiccup_starts['homo1'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[2][1]:[{"start": hiccup_starts["homo2"][i] / 10 * test_duration, "end": hiccup_starts['homo2'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[3][1]:[{"start": hiccup_starts["homo3"][i] / 10 * test_duration, "end": hiccup_starts['homo3'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[4][1]:[{"start": hiccup_starts["homo4"][i] / 10 * test_duration, "end": hiccup_starts['homo4'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[5][1]:[{"start": hiccup_starts["homo5"][i] / 10 * test_duration, "end": hiccup_starts['homo5'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[6][1]:[{"start": hiccup_starts["homo6"][i] / 10 * test_duration, "end": hiccup_starts['homo6'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[7][1]:[{"start": hiccup_starts["homo7"][i] / 10 * test_duration, "end": hiccup_starts['homo7'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[8][1]:[{"start": hiccup_starts["homo8"][i] / 10 * test_duration, "end": hiccup_starts['homo8'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[9][1]:[{"start": hiccup_starts["homo9"][i] / 10 * test_duration, "end": hiccup_starts['homo9'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],
                    nodes[10][1]:[{"start": hiccup_starts["homo10"][i] / 10 * test_duration, "end": hiccup_starts['homo10'][i] / 10 * test_duration + hiccup_duration} for i in range(hiccup_times)],}
print(f'#################hiccup={hiccups_injection}')

#active_sensor_time_slots

#lower_bound test start time , upper_bound test end time, interarrival_rate #expected mean of interarrivals (space between two consecutive events), event_duration #how long each event lasts - constant, seed #start seed (increments per node)
#interarrival_rate 2=95%, 4=72%, 6=66%, 8=50%, 10=41% 12=25%
interarrival_rate = [1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60, 1 * 60,]
#if enabled, interarrival_rate works, otherwise, no interruption happens in workload generations
#get epoch index from file
cmd='grep "epoch" /home/ubuntu/logs/config.txt'
print('read epoch value: ' + cmd)
import utils
out, error = utils.shell(cmd)
print(out + error)
epoch = int(out.split('=')[1])

active_sensor_time_slots = {'enabled': False, 'lower_bound': 0, 'upper_bound': test_duration, 'interarrival_rate': interarrival_rate[epoch], 'event_duration': 5 * 60, 'seed_start': 1,
                            'time_slots': {"homo1":[], "homo2":[], "homo3":[], "homo4":[], "homo5":[], "homo6":[], "homo7":[], "homo8":[], "homo9":[], "homo10":[]},}
import utils
active_sensor_time_slots, percent = utils.active_time_slots_producer(**active_sensor_time_slots)
active_sensor_time_slots['time_slots']['master']=[]
print(f'active_sensor_time_slots=\n{active_sensor_time_slots["time_slots"]}\npercent={percent}')



#copy chart-latest and chart-profile folders to home directory of master
profile_chart = ["chart-profile", "~/charts/chart-profile"]
function_chart = ["chart-latest", "~/charts/chart-latest"]
excel_file_path = "/home/" + getpass.getuser() + "/logs/metrics.xlsx" # this file should already be there with a sheet named nodes

clean_up = True #####
profile_creation_roll_out = 15  #### 30
function_creation_roll_out = 60  # 120


#CPU intensity of applications request per nodes per app
counter=[{"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"10", "short":"5"}] #variable

monitor_interval=10 #second
failure_handler_interval=10
battery_sim_update_interval=10
min_request_generation_interval = 1
sensor_admission_timeout = 3
node_down_sensor_hold_duration = 1 #how long wait after ending the sensor creating. Only applies if battery_sim is True, and node is down. It is useful for SYNC only request when nodes go down to avoid bombarding request generaiton 
max_request_timeout = 15 #max timeout was 30 set for apps, used for timers, failure_handler, etc.

intra_test_cooldown = 10 * 60 # 10 between each epoch to wait for workers
debug=True #master always True
max_cpu_capacity = 3600  #### #actual capacity is 4000m millicpu (or millicores), but 10% is deducted for safety net. Jetson nano and Pi 3 and 4 have 4 cores.

#initial charge value must be turn in to max_battery_charge if > max_battery_charge???
initial_battery_charge = 0 # mwh 0
min_battery_charge = 10 #mwh 125 equals battery charge 10%
min_battery_charge_warmup_percent = 10 #percent default 10 of max_battery_charge 5, 10, 15 , 20
#the pending state of node defined by a time duration after reaching min_battery_charge ("time-based") set by boot_up_delay or defined by a a percentage of battery larger than node has to wait to meet ("warmup-percent-based") set by min_battery_charge_warmup_percent
battery_bootup_strategy = "warmup-percent-based"
max_battery_charge = [ 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250, 1250]#variable #mwh full battery, 9376 - 20% and scale in 1/6: 1250mwh
solar_panel_scale = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,] #it scales renewable input ratio. If 1 the original renewable input value is considered.

#home dir will be attached before this path by pi-agent
#pics folder must be already filled with pics
pics_folder = "/pics-83num-resized-half-6mb-max130kb/" # /pics/
pics_num= 83
file_storage_folder = "/storage/"
#home dir comes before
log_path = "/logs/"

#renewable_input type" real OR poisson
renewable_type = "real"
#renewable input by poisson: set lambda for each nodes
renewable_poisson = [0,0,0,0,0, 0, 0, 0, 0, 0]
#renewable inputs by real dataset: Melbourne CBD in 2018
#for 240 min
# renewable_real={
#     nodes[0][1]:[],
#     nodes[1][1]:[0,0,0,0,0,0,15,60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0],
#     nodes[2][1]:[0,0,0,0,0,0,19,76,101,525,164,679,588,282,484,362,349,269,65,41,0,0,0,0],
#     nodes[3][1]:[0,0,0,0,0,0,36,264,498,454,395,583,546,647,487,399,185,77,88,57,0,0,0,0],
#     nodes[4][1]:[0,0,0,0,0,0,33,59,72,339,353,514,264,991,1025,822,85,129,64,35,0,0,0,0],
#     nodes[5][1]:[0,0,0,0,0,0,38,161,236,458,596,572,480,476,624,894,528,276,85,114,0,0,0,0],
#     nodes[6][1]:[0,0,0,0,0,0,20,73,118,271,361,699,1045,1080,1034,924,769,569,342,77,0,0,0,0],
#     nodes[7][1]:[0,0,0,0,0,0,68,239,448,701,882,999,1063,1051,557,689,249,72,338,134,0,0,0,0],
#     nodes[8][1]:[0,0,0,0,0,0,57,240,474,686,869,994,1066,1080,1036,932,687,575,352,143,0,0,0,0],
#     nodes[9][1]:[0,0,0,0,0,0,76,262,496,681,821,1003,1070,1079,1031,924,764,564,336,133,0,0,0,0],
#     nodes[10][1]:[0,0,0,0,0,0,71,271,505,710,888,1006,1070,1076,1026,916,753,551,322,120,0,0,0,0],
# } #####
#for 180 minutes
renewable_real={
    nodes[0][1]:[],
    nodes[1][1]:[15,60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0],
    nodes[2][1]:[19,76,101,525,164,679,588,282,484,362,349,269,65,41,0,0,0,0],
    nodes[3][1]:[36,264,498,454,395,583,546,647,487,399,185,77,88,57,0,0,0,0],
    nodes[4][1]:[33,59,72,339,353,514,264,991,1025,822,85,129,64,35,0,0,0,0],
    nodes[5][1]:[38,161,236,458,596,572,480,476,624,894,528,276,85,114,0,0,0,0],
    nodes[6][1]:[20,73,118,271,361,699,1045,1080,1034,924,769,569,342,77,0,0,0,0],
    nodes[7][1]:[68,239,448,701,882,999,1063,1051,557,689,249,72,338,134,0,0,0,0],
    nodes[8][1]:[57,240,474,686,869,994,1066,1080,1036,932,687,575,352,143,0,0,0,0],
    nodes[9][1]:[76,262,496,681,821,1003,1070,1079,1031,924,764,564,336,133,0,0,0,0],
   nodes[10][1]:[71,271,505,710,888,1006,1070,1076,1026,916,753,551,322,120,0,0,0,0],
} #####

#120
# renewable_real={
#     nodes[0][1]:[],
#     nodes[1][1]:[60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0],
#     nodes[2][1]:[76,101,525,164,679,588,282,484,362,349,269,65,41,0,0,0,0],
#     nodes[3][1]:[264,498,454,395,583,546,647,487,399,185,77,88,57,0,0,0,0],
#     nodes[4][1]:[59,72,339,353,514,264,991,1025,822,85,129,64,35,0,0,0,0],
#     nodes[5][1]:[161,236,458,596,572,480,476,624,894,528,276,85,114,0,0,0,0],
#     nodes[6][1]:[73,118,271,361,699,1045,1080,1034,924,769,569,342,77,0,0,0,0],
#     nodes[7][1]:[239,448,701,882,999,1063,1051,557,689,249,72,338,134,0,0,0,0],
#     nodes[8][1]:[240,474,686,869,994,1066,1080,1036,932,687,575,352,143,0,0,0,0],
#     nodes[9][1]:[262,496,681,821,1003,1070,1079,1031,924,764,564,336,133,0,0,0,0],
#    nodes[10][1]:[271,505,710,888,1006,1070,1076,1026,916,753,551,322,120,0,0,0,0],
# } #####
#default=4 not sure if effective by updating on the fly
waitress_threads = 10
#NOTE:function name and queue name pattern is "node_name-function_name" like "w1-irrigation"
#Node_role: #MASTER #LOAD_GENERATOR #STANDALONE #MONITOR

#scheduling is based on requests, not limits


#default SSD 1800 1800
app_cpu_quote = {"ssd":["1800m", "1800m"],
                "yolo3":["3000m", "3000m"],
                "irrigation": ["600m", "600m"],
                "crop-monitor": ["450m", "450m"],
                "short": ["100m", "100m"]}
# app_cpu_quote = {"ssd":["1000m", "3600m"],
#                 "yolo3":["3000m", "3000m"],
#                 "irrigation": ["600m", "600m"],
#                 "crop-monitor": ["450m", "450m"],
#                 "short": ["100m", "100m"]}
app_memory_quote = {"ssd":["50M", "3000M"],
                    "yolo3":["500M", "500M"],
                    "irrigation": ["40M", "40M"],
                    "crop-monitor": ["30M", "30M"],
                    "short": ["200M", "200M"]}
# app_memory_quote = {"ssd":["500M", "3000M"],
#                     "yolo3":["500M", "500M"],
#                     "irrigation": ["40M", "40M"],
#                     "crop-monitor": ["30M", "30M"],
#                     "short": ["200M", "200M"]}

#function_timeouts = {'yolo3':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'irrigation':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'crop-monitor':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'short':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'}}
#function_timeout['yolo3']['read'], function_timeout['yolo3']['write'],
#function_timeout['yolo3']['exec'],function_timeout['yolo3']['handlerWait']

#USB METERs: Pair before tests
# usb_meter={"master":"",
#            nodes[0][1]:"00:15:A5:00:03:E7",
#            nodes[1][1]:"00:15:A3:00:56:0F",
#            nodes[2][1]:"00:15:A3:00:52:2B",
#            nodes[3][1]:"00:15:A3:00:19:A7",
#            nodes[4][1]:"00:15:A3:00:5A:6F",
#            nodes[5][1]:"",
#            nodes[6][1]:"00:16:A5:00:0E:94"}
usb_meter={ nodes[0][1]:"",
            nodes[1][1]:"00:16:A6:00:26:09",
            nodes[2][1]:"00:16:A5:00:14:FA",
            nodes[3][1]:"00:16:A6:00:21:4D",
            nodes[4][1]:"00:16:A5:00:0C:8E",
            nodes[5][1]:"00:16:A6:00:26:63",
            nodes[6][1]:"00:15:A5:00:03:E7",
            nodes[7][1]:"00:15:A3:00:56:0F",
            nodes[8][1]:"00:15:A3:00:52:2B",
            nodes[9][1]:"00:15:A3:00:19:A7",
            nodes[10][1]:"00:15:A3:00:5A:6F",}

#broken USB meter: "00:15:A5:00:02:ED", "00:15:A3:00:68:C4"
#either battery_operated or battery_sim should be enabled
battery_operated = {nodes[0][1]: False, nodes[1][1]: False, nodes[2][1]: False,nodes[3][1]: False,nodes[4][1]: False,nodes[5][1]: False,nodes[6][1]: False,nodes[7][1]: False,nodes[8][1]: False,nodes[9][1]: False,nodes[10][1]: False} #means pijuice operated
battery_sim = {nodes[0][1]: False, nodes[1][1]: True, nodes[2][1]: True,nodes[3][1]: True,nodes[4][1]: True, nodes[5][1]: True, nodes[6][1]: True, nodes[7][1]: True, nodes[8][1]: True, nodes[9][1]: True, nodes[10][1]: True}

#autoscaling
scale_to_zero = False #(not implemented yet)

#auto-scaling:  "openfaas"  or "hpa"
auto_scaling = "hpa"
#if HPA is used only
autoscaling_interval = 10* 60
#factor: default is 20, if 0, if hpa, auto-scaling by hpa, otherwise openfaas scaling is disabled
auto_scaling_factor = 100
#if HPA is used, function objects get 1 for both min and max, instead HPA object applies these values.
min_replicas = {"ssd": 1, "yolo3": 1, "crop-monitor":2, "irrigation":2, "short":1}
max_replicas = {"ssd": 1, "yolo3": 3, "crop-monitor":2, "irrigation":2, "short":10} ####
#if HPA is used, set avg CPU utilization condition
avg_cpu_utilization = 20
#if HPA is used, set scale down stabilaztion window
scale_down_stabilizationWindowSeconds = 60
            
# network_name_server={'update': False, 'new_value': '8.8.8.8'}            
#'off' always off, 'on_if_attachement' only on if attachment is connected to the device like TPU, 'on' keep them up anyway
#On Pi, usb ports and Ethernet turn off/on together
usb_eth_ports = 'on'
#re-boot-at-start or 're-execute-at-start' agents (peers) at the beginning of each experiment (as of second test onward), 
#if 'reboot-at-end' is in the value, metrics_sender uses it to reboot the node after sending metrics at the end
agents_reuse='re-boot-at-start'
agents_bootup_sec = 30 

#after test is done and cooldown is done, master can do 2 approaches if another test is left:
#Default: 'continue': call launcher for new test 
# 'reboot-before-starting-next-test': save epoch indentifier in config.txt file, reboot itself. after booting up, it runs launcher, but launcher reads epoch value from config.txt
#if reboot, this file must be placed first echo "epoch=0" >  /home/ubuntu/logs/config.txt

master_behavior_after_test_if_multiple_tests = 'reboot-before-starting-next-test'
cluster_info_populate={'enable': True, 'interval': 30, 'log_on_file':{'enable': True, 'path': '/home/ubuntu/logs/cluster_info/'}}

#Plan by node names
plans = {}
# plan={
# "master":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"MASTER",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["master"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8]func_info -->[min,max,memory requests, memory limits, cpu request, cpu limit, env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile, version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg[nodes[0][1]][0], nodes[0][1] + '-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg[nodes[0][1]][1], nodes[0][1] + '-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg[nodes[0][1]][2], nodes[0][1] + '-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg[nodes[0][1]][3], nodes[0][1] + '-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg[nodes[0][1]][4], nodes[0][1] + '-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown", "unknown"]]],
#     "peers":[],
#     "usb_meter_involved":False,
#     "battery_operated":battery_operated[nodes[0][1]],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim[nodes[0][1]], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[0]], renewable_real[nodes[0][1]],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":True,
#     "cpu_freq_config": cpu_freq_config,},
# }

#costruct nodes
for node in nodes:
    #node = ["PEER", "w2","10.0.0.92"]
    node_name = node[1]
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    node_role = 'MASTER' if node[1] == 'master' else 'LOAD_GENERATOR'
    # if node[0] == "PEER":

    plans[node_name] = {
        "test_name": "",
        "node_role": node_role,
        "load_balancing": load_balancing,
        "debug":True,
        "bluetooth_addr":usb_meter[node_name],
        "hiccups_injection":  hiccups_injection[node_name],
        "active_sensor_time_slots": active_sensor_time_slots,
        #[0]app name
        #[1] run/not
        #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
        #[3] workload_cfg
        #[4] func_name [5] func_data [6] sent [7] recv
        #[8][min,max,mem requests,mem limits, cpu req, cpu limits,counter, redisServerIp, redisServerPort,
        #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version,image
        #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
            # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
            # podAntiAffinity_required_functionName
        "apps":[
            ['ssd', apps["ssd"], workload_type, workload_cfg[node_name][0], node_name + '-ssd', 'reference', 0, 0,
            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
                ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
                ["unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
            ['yolo3', apps["yolo3"], workload_type, workload_cfg[node_name][1], node_name + '-yolo3', 'reference', 0, 0,
            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
                ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
                ["unknown", "unknown","unknown", "unknown", "unknown","unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
            ['irrigation', apps["irrigation"], workload_type, workload_cfg[node_name][2], node_name + '-irrigation', 'reference', 0, 0,
            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
                ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
                ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
            ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg[node_name][3], node_name + '-crop-monitor', 'reference', 0, 0,
            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
                ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
                ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
            ['short', apps["short"], workload_type, workload_cfg[node_name][4], node_name + '-short', 'reference', 0, 0,
            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
                ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
                ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
        "peers":[],
        "usb_meter_involved":True if node_role == 'LOAD_GENERATOR' else False,
        "battery_operated":battery_operated[node_name],
        #0: battery_sim True/False, 1:max (variable), 2:initial #3current SoC,
        #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 min_battery_charge, 9 turned on at,10 soc_unlimited, 11 battery_excess_input_mwh per charge input mwh
        #12: status {}, 13: energy_input, 14: energy_consumed, 15: battery_bootup_strategy, 16: min_battery_charge_warmup_percent, 17: solar_panel_scale
        "battery_cfg":[battery_sim[node_name], 0,initial_battery_charge, initial_battery_charge,
            renewable_type,[seed,renewable_poisson[0]], renewable_real[node_name],
            battery_sim_update_interval, min_battery_charge, 0, initial_battery_charge, 0, {}, 0, 0, battery_bootup_strategy, min_battery_charge_warmup_percent, solar_panel_scale],
        "time_based_termination":[True, test_duration],
        "monitor_interval":monitor_interval,
        "failure_handler_interval":failure_handler_interval,
        "max_request_timeout":max_request_timeout,
        "min_request_generation_interval": min_request_generation_interval,
        "session_enabled": session_enabled,
        "sensor_admission_timeout": sensor_admission_timeout,
        "node_down_sensor_hold_duration": node_down_sensor_hold_duration,
        "max_cpu_capacity": max_cpu_capacity,
        "log_path": log_path,
        "pics_folder":pics_folder,
        "pics_num": pics_num,
        "file_storage_folder":file_storage_folder,
        "waitress_threads": waitress_threads,
        "boot_up_delay": boot_up_delay,
        #only master is True
        "raspbian_upgrade_error": True if node_role == 'LOAD_GENERATOR' else True,
        "cpu_freq_config": cpu_freq_config,
        "usb_eth_ports": usb_eth_ports,}
#        "network_name_server": network_name_server,
    
# #w1
# "w1":
# {
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w1"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,mem requests,mem limits, cpu req, cpu limits,counter, redisServerIp, redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version,image
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w1"][0], 'w1-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w1"][1], 'w1-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w1"][2], 'w1-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w1"][3], 'w1-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w1"][4], 'w1-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w1"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge, 9 turned on at
#     "battery_cfg":[battery_sim["w1"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[0]], renewable_real["w1"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},

# #w2
# "w2":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w2"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#         #??????unknown refer to profiles in openfaas and is only for filtering maximum of 5 nodes. 
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w2"][0], 'w2-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0,  apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w2"][0], 'w2-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0,  apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w2"][1], 'w2-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w2"][2], 'w2-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w2"][3], 'w2-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w2"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim["w2"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[1]], renewable_real["w2"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},

# #w3
# "w3":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w3"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w3"][0], 'w3-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w3"][0], 'w3-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w3"][1], 'w3-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w3"][2], 'w3-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w3"][3], 'w3-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w3"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim["w3"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[2]], renewable_real["w3"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},

# #w4
# "w4":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w4"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w4"][0], 'w4-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w4"][0], 'w4-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w4"][1], 'w4-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w4"][2], 'w4-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w4"][3], 'w4-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w4"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge, 9 turned on at
#     "battery_cfg":[battery_sim["w4"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[3]], renewable_real["w4"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},

# #w5
# "w5":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w5"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w5"][0], 'w5-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w5"][0], 'w5-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w5"][1], 'w5-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w5"][2], 'w5-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w5"][3], 'w5-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w5"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim["w5"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[4]], renewable_real["w5"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},

# #w6
# "w6":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w6"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w6"][0], 'w6-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w6"][0], 'w6-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w6"][1], 'w6-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w6"][2], 'w6-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w6"][3], 'w6-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w6"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim["w6"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[4]], renewable_real["w6"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,},
# #w7
# "w7":{
#     "test_name": "",
#     #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
#     "node_role":"LOAD_GENERATOR",
#     "load_balancing": load_balancing,
#     "debug":True,
#     "bluetooth_addr":usb_meter["w7"],
#     #[0]app name
#     #[1] run/not
#     #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
#     #[3] workload_cfg
#     #[4] func_name [5] func_data [6] sent [7] recv
#     #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
#     #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
#     #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
#         # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
#         # podAntiAffinity_required_functionName
#     "apps":[
#         ['ssd', apps["ssd"], workload_type, workload_cfg["w7"][0], 'w7-ssd', 'reference', 0, 0,
#            [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['yolo3', apps["yolo3"], workload_type, workload_cfg["w7"][0], 'w7-yolo3', 'reference', 0, 0,
#            [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['irrigation', apps["irrigation"], workload_type, workload_cfg["w7"][1], 'w7-irrigation', 'reference', 0, 0,
#            [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w7"][2], 'w7-crop-monitor', 'reference', 0, 0,
#            [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
#         ['short', apps["short"], workload_type, workload_cfg["w7"][3], 'w7-short', 'reference', 0, 0,
#            [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
#             ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
#              ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
#     "peers":[],
#     "usb_meter_involved":True,
#     "battery_operated":battery_operated["w7"],
#     #1:max,2:initial #3current SoC,
#     #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
#     "battery_cfg":[battery_sim["w7"], 0,initial_battery_charge, initial_battery_charge,
#         renewable_type,[seed,renewable_poisson[4]], renewable_real["w7"],
#         battery_sim_update_interval, min_battery_charge, 0],
#     "time_based_termination":[True, test_duration],
#     "monitor_interval":monitor_interval,
#     "failure_handler_interval":failure_handler_interval,
#     "max_request_timeout":max_request_timeout,
#     "min_request_generation_interval": min_request_generation_interval,
#     "session_enabled": session_enabled,
#     "sensor_admission_timeout": sensor_admission_timeout,
#     "max_cpu_capacity": max_cpu_capacity,
#     "log_path": log_path,
#     "pics_folder":pics_folder,
#     "pics_num": pics_num,
#     "file_storage_folder":file_storage_folder,
#     "waitress_threads": waitress_threads,
#     "boot_up_delay": boot_up_delay,
#     #only master is True
#     "raspbian_upgrade_error":False,
#     "cpu_freq_config": cpu_freq_config,}
# }


#openfaas setup chart 8.0.4
#Gateway: version 0.21.1
#replicas: 5, direct_functions=false, read_timeout:35s, write_timeout: 35s, upstream_timeout: 30s, operator:true, read_timeout: 30s, write_timeout: 30s

#gueue: version per app
#replicas: 2, ack_wait: 30s, max_inflight: 100, max_retry_attempt: 1, max_retry_wait: 10s, retry_http_code: 429,,
