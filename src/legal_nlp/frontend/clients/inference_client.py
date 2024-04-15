import json
from fastapi import websockets
import requests
import time
from config import Config

class InferenceClient:
    def __init__(self):
        self.chat_uri = Config.INFERENCE_CHAT_URI + "/api/v1/chat"
        self.stream_uri = Config.INFERENCE_STREAM_URI + "/api/v2/stream"


    def queue_async_job(self, messages, stream=False,  generation_args={}, prompt=None):
        if stream:
            yield from self.get_gpt_stream(messages, generation_args=generation_args, prompt=prompt)
        else:
            return self.get_gpt_response(messages, generation_args=generation_args, prompt=prompt)


    def get_gpt_stream(self, messages, generation_args={}, prompt=None):
        data = {
            "messages": messages,
            "seed": generation_args.get('seed', 10),
            "max_tokens": generation_args.get('max_tokens', 512),
            "temperature": generation_args.get('temperature', 0.8),
            "top_p": generation_args.get('top_p', 0.7),
            "repetition_penalty": generation_args.get('repetition_penalty', 1.05),
            "top_k": generation_args.get('top_k', 30),
            "add_bos_token": generation_args.get('add_bos_token', False),
            "use_lora": generation_args.get('use_lora', False),
            "prompt": prompt
        }
        
        with websockets.connect(self.stream_uri, ping_interval=None) as websocket:
            websocket.send(json.dumps(data))

            while True:
                incoming_data = websocket.recv()
                incoming_data = json.loads(incoming_data)

                match incoming_data["event"]:
                    case "text_stream":
                        yield incoming_data["text"]
                    case "stream_end":
                        return


    def get_gpt_response(self, messages, generation_args={}, prompt=None):
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "messages": messages,
            "seed": generation_args.get('seed', 10),
            "max_tokens": generation_args.get('max_tokens', 512),
            "temperature": generation_args.get('temperature', 0.8),
            "top_p": generation_args.get('top_p', 0.7),
            "repetition_penalty": generation_args.get('repetition_penalty', 1.05),
            "top_k": generation_args.get('top_k', 30),
            "add_bos_token": generation_args.get('add_bos_token', False),
            "use_lora": generation_args.get('use_lora', False),
            "prompt": prompt
        }
        response = requests.post(self.chat_uri, headers=headers, json=data, verify=True)
        
        return response.json()['response']
