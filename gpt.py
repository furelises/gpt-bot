import json
import logging
import os
from pathlib import Path

import requests
from transformers import AutoTokenizer

import config


class GPTResponse:
    def __init__(self, status: bool, message: str):
        self.status = status
        self.message = message


class GPT:
    def __init__(self, system_content: str):
        self.system_content = system_content
        self.URL = config.gpt_url
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = int(config.gpt_max_tokens)

    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained(config.gpt_model)
        return len(tokenizer.encode(prompt))

    def __parse_resp(self, response) -> GPTResponse:
        if response.status_code < 200 or response.status_code >= 300:
            return GPTResponse(False, f"Ошибка: {response.status_code}")

        try:
            full_response = response.json()
        except Exception as e:
            logging.error('Ошибка запроса к gpt: %s', repr(e))
            return GPTResponse(False, "Ошибка получения JSON")

        if "error" in full_response or 'choices' not in full_response:
            return GPTResponse(False, f"Ошибка: {full_response}")

        result = full_response['choices'][0]['message']['content']

        if result == "":
            logging.info("Объяснение закончено")

        return GPTResponse(True, result)

    def __make_promt(self, user_request, assistant_content):
        return {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": assistant_content},
            ],
            "temperature": 1,
            "max_tokens": self.MAX_TOKENS,
        }

    def send_request(self, user_request, assistant_content: "") -> GPTResponse:
        if assistant_content == "":
            assistant_content = " "
        # отладка сообщения об ошибке
        if user_request == "debug error":
            logging.info("обработка отладочного сообщения")
            return GPTResponse(False, "упс...")

        logging.info("Отправка запроса gpt: %s", user_request)
        response_json = self.__make_promt(user_request, assistant_content)
        try:
            resp = requests.post(url=self.URL, headers=self.HEADERS, json=response_json)
        except Exception as e:
            logging.error('Ошибка запроса к gpt: %s', repr(e))
            return GPTResponse(False, "Ошибка запроса")

        response = self.__parse_resp(resp)
        return response
