# yttg
Telegram bot that uploads audio for posted videos URLs. Also it can be added to authorized channels

## Environment variables
  * `TOKEN` (required) – bot token
  * `USERS` (required, can be an empty list `[]`) – list of allowed user ids (`[user_id1, user_id2]`)
  * `CHATS` (required, can be an empty list `[]`) – list of allowed chat ids (`[chat_id1, chat_id2]`)
  * `PROXY` (optional) – network proxy that is used if `HTTPS_PROXY`/`https_proxy` variable is not set. Can be socks5 proxy

 If you are not using docker image then script needs `MEDIADIR` environment variable that points to the temporary download directory
