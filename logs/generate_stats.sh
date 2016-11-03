
won=$(cat $1 | awk '{print $4}' | grep 1 | wc -l)

total=$(cat $1 | awk '{print $4}' | grep -E '1|2' | wc -l)

win_rate=$(bc <<< "scale=2;$won/$total")

echo "Player 1 won: " $win_rate "% games"
