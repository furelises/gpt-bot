from dotenv import dotenv_values

config = dotenv_values(".env")

telegram_token = config['telegram_token']
gpt_url = config['gpt_url']
gpt_max_tokens = config['gpt_max_tokens']
gpt_assistant_content = config['gpt_assistant_content']
gpt_model = config['gpt_model']
db_file = config['db_file']
log_file = config['log_file']

PROMPTS_TEMPLATES = {
    '/help_with_maths': {
        'beginner': "Ты помощник по математике, давай простые ответы на русском языке.",
        'advanced': "Ты помощник по математике, давай сложные ответы на русском языке."
    },
    '/help_with_cook': {
        'beginner': "Ты помощник по кулинарии, давай простые ответы на русском языке.",
        'advanced': "Ты помощник по кулинарии, давай сложные ответы на русском языке."
    }
}


def get_gpt_system_content(subject, level):
    return PROMPTS_TEMPLATES.get(subject, {}).get(level, None)
