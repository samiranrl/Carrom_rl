for i in `seq 1 1`; do
    echo "Turn: $i"
    gnome-terminal -e "python Server.py $1 $2"
    gnome-terminal -e "python Agent.py "
    wait
done
