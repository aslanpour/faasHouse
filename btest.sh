for i in {0..9}
do 
	echo "Send to 10.0.0.8$i"
	timeout 1s curl 10.0.0.8$i:5000/test || echo "FAILED ****************** 10.0.0.8$i"
done
