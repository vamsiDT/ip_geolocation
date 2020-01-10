#rm ips1.txt
for J in $(cat ips.txt);do
echo "$J"
a=$(sudo ping -c 10 -i 0.000001 $J -w 2> /tmp/xc; cat /tmp/xc |tail -n1 | awk '{print $4}' | awk -F "/" '{print $1}')
#echo $a
if [[ "$a" != 0 ]];then
echo  "$J" >> ips1.txt
fi
#IP=$I
#echo "$IP"
#COUNTRY=$(geoiplookup $IP | awk '{print $5}')
#sudo ping $IP -c 100 -i 0.0000001 > /tmp/xc
#AVG_RTT=$(cat /tmp/xc | tail -n1 | awk '{print $4}' | awk -F "/" '{print $2}')
#echo -e "ip:\t$IP\tcountry:$COUNTRY\tavg_rtt:$AVG_RTT"
done
