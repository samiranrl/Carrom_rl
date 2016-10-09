for((c=1;c<=50;c++))
do
python ServerP1.py -p 34345 -rs $c -s 1 &
sleep 1
python Agent_Random_Aim.py -p 34345  &
sleep 30
done
