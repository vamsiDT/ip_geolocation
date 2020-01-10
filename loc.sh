I=$1
for J in $(cat working_nodes.dat);do
a=$(ssh -o "StrictHostKeyChecking no" -l upmc_netmet $J sudo ping -c 10 -i 0.000001 $I -w 2 > /tmp/xc; cat /tmp/xc |tail -n1 | awk '{print $4}' | awk -F "/" '{print $1}')
#if [ $a -gt 0 ];then
echo "node,$J,minrtt,$a"
#fi
#IP=$I
#echo "$IP"
#COUNTRY=$(geoiplookup $IP | awk '{print $5}')
#sudo ping $IP -c 100 -i 0.0000001 > /tmp/xc
#AVG_RTT=$(cat /tmp/xc | tail -n1 | awk '{print $4}' | awk -F "/" '{print $2}')
#echo -e "ip:\t$IP\tcountry:$COUNTRY\tavg_rtt:$AVG_RTT"
done
