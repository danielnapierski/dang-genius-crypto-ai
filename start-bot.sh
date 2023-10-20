# shellcheck disable=SC2028
printf 'Starting bot...\nSee bot.log.txt'
python3 -c 'from dang_genius.bot import bot; bot()' >> bot.log.txt
