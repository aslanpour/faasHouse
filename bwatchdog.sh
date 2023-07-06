# Define the commands to run
commands="
sudo sed -i 's/#ShutdownWatchdogSec=10min/ShutdownWatchdogSec=10min/' /etc/systemd/system.conf
sudo sed -i 's/#RebootWatchdogSec=10min/RebootWatchdogSec=10min/' /etc/systemd/system.conf
sudo sed -i 's/#RuntimeWatchdogSec=10/RuntimeWatchdogSec=15/' /etc/systemd/system.conf
"

# Loop over the list of IP addresses and run the commands
for i in {80..89}
do
    ip="10.0.0.$i"
    echo "Running commands on $ip"
    ssh -o "StrictHostKeyChecking no" "$ip" "echo '$commands' | while read command; do eval \"\$command\"; done"
done
