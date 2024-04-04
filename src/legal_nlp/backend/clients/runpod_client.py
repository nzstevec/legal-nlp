import requests
import time
from config import Config

class RunpodClient:
    def __init__(self):
        self.base_uri = Config.RUNPOD_BASE_URI
        self.bearer_token = Config.RUNPOD_BEARER_TOKEN
        self.status_check_delay = Config.RUNPOD_STATUS_CHECK_DELAY
        self.stream_delay = Config.RUNPOD_STREAM_DELAY

    def get_stream_output(self, stream_endpoint, headers):
        stream_response = requests.get(stream_endpoint, headers=headers)
        stream_json = stream_response.json()
        output = [x["output"] for x in stream_json["stream"]]
        return output

    def queue_async_job(self, messages, stream=False,  generation_args={}):
        endpoint = f"{self.base_uri}/run"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

        data = {
            "input": {
                "messages": messages,
                "seed": generation_args.get('seed', 10),
                "max_tokens": generation_args.get('max_tokens', 512),
                "temperature": generation_args.get('temperature', 0.8),
                "top_p": generation_args.get('top_p', 0.7),
                "repetition_penalty": generation_args.get('repetition_penalty', 1.05),
                "top_k": generation_args.get('top_k', 30),
                "add_bos_token": generation_args.get('add_bos_token', False),
                "use_lora": generation_args.get('use_lora', False),
            }
        }

        # Queue up job
        response = requests.post(endpoint, headers=headers, json=data, verify=True)
        response.raise_for_status()
        
        jobId = response.json()['id']
        status_endpoint = f"{self.base_uri}/status/{jobId}"
        stream_endpoint = f"{self.base_uri}/stream/{jobId}"
        
        status = {'id': jobId, 'status': "IN_QUEUE"}
        
        # Wait for job to finish
        while (status['status'] == "IN_QUEUE" or status['status'] == "IN_PROGRESS"):
            # Query job status
            status_response = requests.get(status_endpoint, headers=headers)
            status_response.raise_for_status()
            status = status_response.json()
            
            if stream:
                output = self.get_stream_output(stream_endpoint, headers)
                yield "".join(output)
                time.sleep(self.stream_delay)
            else:
                time.sleep(self.status_check_delay)

        if stream:
            output = self.get_stream_output(stream_endpoint, headers)
            yield "".join(output)
        else:
            yield status['output']['response']

    def get_gpt_response(self, messages, generation_args={}):
        response = ""
        response_generator = self.queue_async_job(messages, stream=False,  generation_args=generation_args)
        for message in response_generator:
            response += message
        
        return message