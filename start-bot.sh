# shellcheck disable=SC2028
printf 'Starting bot...\nSee bot.log.txt'
date +%Y-%m-%d_%H:%M:%S
python3 -c 'from dang_genius.bot import bot; bot()' >> bot.log.txt
