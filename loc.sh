I=$1
for J in $(cat working_nodes.dat);do

#b=0
#N=0
#while [[ $b -le 0 && $N -le 3 ]];do
# echo "## ping ##"
a=$(ssh -o "StrictHostKeyChecking no" -o "PasswordAuthentication no" -o "ConnectTimeout 4" -l upmc_netmet $J sudo ping -c 10 -i 0.000001 $I -w 2 > /tmp/xc; cat /tmp/xc |tail -n1 | awk '{print $4}' | awk -F "/" '{print $1}')
#N=$(( $N+1 ))
#b=$(echo $a | awk -F "." '{print $1}')
# echo $a
sleep 1
#done


#B=-1
#N=0
#while [[ $B -le 0 && $N -le 3 ]];do
# echo "## traceroute ##"
B=$(ssh -o "StrictHostKeyChecking no"  -o "PasswordAuthentication no" -o "ConnectTimeout 4" -l upmc_netmet $J traceroute $I 2>/dev/null > /tmp/xc1; cat /tmp/xc1 |wc -l)
B=$(( $B-1 ))
B=$(python -c "print($B*1.0)")
#N=$(( $N+1 ))
# echo "$hops: B"
sleep 1
#done

#if [ $a -gt 0 ];then

echo "node,$J,minrtt,$a,hops,$B"

#fi
#IP=$I
#echo "$IP"
#COUNTRY=$(geoiplookup $IP | awk '{print $5}')
#sudo ping $IP -c 100 -i 0.0000001 > /tmp/xc
#AVG_RTT=$(cat /tmp/xc | tail -n1 | awk '{print $4}' | awk -F "/" '{print $2}')
#echo -e "ip:\t$IP\tcountry:$COUNTRY\tavg_rtt:$AVG_RTT"
done
