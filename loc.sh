for I in $(cat ips.txt);do
IP=$I
echo "$IP"
COUNTRY=$(geoiplookup $IP | awk '{print $5}')
sudo ping $IP -c 100 -i 0.0000001 > /tmp/xc
AVG_RTT=$(cat /tmp/xc | tail -n1 | awk '{print $4}' | awk -F "/" '{print $2}')
echo -e "ip:\t$IP\tcountry:$COUNTRY\tavg_rtt:$AVG_RTT"
done
