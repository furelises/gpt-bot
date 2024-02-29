import os
from pathlib import Path
import json

import requests
from transformers import AutoTokenizer

import env


class GPTResponse:
    def __init__(self, status: bool, message: str):
        self.status = status
        self.message = message


class GPT:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.system_content = env.gpt_system_content
        self.URL = env.gpt_url
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = int(env.gpt_max_tokens)
        self.assistant_content = []
        self.last_error_message = ""
        self.__restore()

    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained(env.gpt_model)
        return len(tokenizer.encode(prompt))

    def __parse_resp(self, response) -> GPTResponse:
        if response.status_code < 200 or response.status_code >= 300:
            self.__clear_history()
            return GPTResponse(False, f"Ошибка: {response.status_code}")

        try:
            full_response = response.json()
        except:
            self.__clear_history()
            return GPTResponse(False, "Ошибка получения JSON")

        if "error" in full_response or 'choices' not in full_response:
            self.__clear_history()
            return GPTResponse(False, f"Ошибка: {full_response}")

        result = full_response['choices'][0]['message']['content']

        if result == "":
            print("Объяснение закончено")
            self.__clear_history()
        else:
            self.__save_history(result)

        return GPTResponse(True, self.assistant_content[-1])

    def __make_promt(self, user_request):
        json = {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": " ".join(self.assistant_content)},
            ],
            "temperature": 1,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    def send_request(self, user_request) -> GPTResponse:
        # отладка сообщения об ошибке
        if user_request == "debug error":
            self.last_error_message = "unknown error"
            self.__dump()
            return GPTResponse(False, self.last_error_message)

        json = self.__make_promt(user_request)
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        response =  self.__parse_resp(resp)
        if not response.status:
            self.last_error_message = response.message
        return response

    def __save_history(self, content_response):
        self.assistant_content.append(content_response)
        self.last_error_message = ""
        self.__dump()

    def __clear_history(self):
        self.assistant_content = [env.gpt_assistant_content]
        self.last_error_message = ""
        self.__dump()

    def __get_file(self):
        return Path(f"{env.db_path}/{self.user_id}.json")

    def __dump(self):
        file = self.__get_file()
        maps = {
            "assistant_content": self.assistant_content,
            "last_error_message": self.last_error_message,
        }
        with open(file, "w") as f:
            json.dump(maps, f)

    def __restore(self):
        file = self.__get_file()
        if os.path.exists(file):
            with open(self.__get_file(), "r") as f:
                maps = json.load(f)
                self.assistant_content = maps.get("assistant_content", [])
                self.last_error_message = maps.get("last_error_message", "")
        if not self.assistant_content:
            self.assistant_content = [env.gpt_assistant_content]
