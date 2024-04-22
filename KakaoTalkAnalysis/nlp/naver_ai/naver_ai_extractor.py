import json
import requests


class NaverAIExtractor:
    def __init__(self, naver_ai_private) -> None:
        self.header = self.__set_header(naver_ai_private)

    def extract_sentimental(self, content):
        base_url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
        body = self.__get_sentimental_body(content)
        resp = requests.post(
            url=base_url, headers=self.header, data=json.dumps(body)
        )
        return resp.json()

    def __get_sentimental_body(self, content):
        body = {
            "content": "",
        }
        body["content"] = content
        return body

    def extract_summary(self, content):
        base_url = (
            "https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize"
        )
        body = self.__get_summary_body(content)
        resp = requests.post(
            url=base_url, headers=self.header, data=json.dumps(body)
        )
        return resp.json()

    def __get_summary_body(self, content):
        body = {
            "document": {
                "content": {},
            },
            "option": {
                "language": "ko",
                "model": "general",
                "tone": 0,
                "summaryCount": 3,
            },
        }
        body["document"]["content"] = content
        return body

    def __set_header(self, naver_ai_private):
        header = {
            "X-NCP-APIGW-API-KEY-ID": naver_ai_private["client_id"],
            "X-NCP-APIGW-API-KEY": naver_ai_private["client_secret"],
            "Content-Type": naver_ai_private["content_type"],
        }
        return header
