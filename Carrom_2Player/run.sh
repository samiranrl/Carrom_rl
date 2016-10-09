for((c=1;c<=30;c++))
do
python ServerP2.py -rs $c -s 1 &
sleep 1
python Agent_Random_Aim.py -p 12121  &
sleep 1
python Agent_improved.py -p 34343  &
sleep 25
done
