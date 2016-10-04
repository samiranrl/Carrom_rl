for i in `seq 1 10`; do
    echo "Turn: $i"
    python Server.py $1 $2
    sleep 5
    python Agent.py 
    wait
done
