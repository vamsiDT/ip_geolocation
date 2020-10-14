for I in $(cat working_nodes.dat);do
	for J in $(cat all_working_nodes.dat);do
		if [ "$I" != "$J" ];then
			#echo "from $I ping $J"
			A=$(ssh -o "StrictHostKeyChecking no"  -o "PasswordAuthentication no" -o "ConnectTimeout 4" -l upmc_netmet $I sudo ping -i 0.000001 -c 100 $J -w 2 > /tmp/xc; cat /tmp/xc |tail -n1 | awk '{print $4}' | awk -F "/" '{print $1}')
			#echo "from $I traceroute $J"
			B=$(ssh -o "StrictHostKeyChecking no"  -o "PasswordAuthentication no" -o "ConnectTimeout 4" -l upmc_netmet $I traceroute -w 0.5 $J 2>/dev/null > /tmp/xc3; cat /tmp/xc3 | grep "ms" |wc -l)
			#B=$(( $B-1 ))
			echo  "host,$I,host,$J,rtt,$A,hops,$B"
		fi
	#echo -e "host:\t$I\thost:\t$J\trtt:\t$A"
	done
done
