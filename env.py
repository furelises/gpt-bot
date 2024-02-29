from dotenv import dotenv_values

config = dotenv_values(".env")

telegram_token = config['telegram_token']
gpt_url = config['gpt_url']
gpt_max_tokens = config['gpt_max_tokens']
gpt_system_content = config['gpt_system_content']
gpt_assistant_content = config['gpt_assistant_content']
gpt_model = config['gpt_model']
db_path = config['db_path']
