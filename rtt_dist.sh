for I in $(cat working_nodes.dat);do
	for J in $(cat working_nodes.dat);do
		if [ "$I" != "$J" ];then
			A=$(ssh -o "StrictHostKeyChecking no" -l upmc_netmet $I sudo ping -i 0.000001 -c 100 $J  > /tmp/xc; cat /tmp/xc |tail -n1 | awk '{print $4}' | awk -F "/" '{print $1}')
			echo  "host:\t$I\thost:\t$J\trtt:\t$A"
		fi
	#echo -e "host:\t$I\thost:\t$J\trtt:\t$A"
	done
done
