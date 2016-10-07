for((c=1;c<=3;c++))
do
python ServerP2.py 0 &
sleep 5
python Agent_improved.py &
python Agent_improved2.py &
sleep 90
done
