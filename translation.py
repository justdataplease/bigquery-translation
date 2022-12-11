import requests, uuid, json
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class Translator:
    def __init__(self):
        """
        Example:
        translator = Translator()
        print(translator.translate_text(text="let me go in", to_language='el'))
        """
        # Set up the credentials for the Translator Text API
        # Add your key and endpoint
        # self.key = config('AZURE_TRANSLATION_KEY')
        # self.location = config('AZURE_TRANSLATION_LOCATION')
        self.key = os.getenv('AZURE_TRANSLATION_KEY')
        self.location = os.getenv('AZURE_TRANSLATION_LOCATION')
        self.constructed_url = "https://api.cognitive.microsofttranslator.com/translate"
        self.api_version = '3.0'

    def translate_text(self, text: str, to_language: str, from_language: str = False) -> str:
        """
        Translate function
        :param text: text to translate.
        :param to_language: desired language to translate to.
        :param from_language: origin language. if from_language is not defined then api will detect language.
        :return:
        """
        try:
            params = {
                'api-version': self.api_version,
                'to': [to_language]
            }
            if from_language:
                params['from'] = from_language

            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                # location required if you're using a multi-service or regional (not global) resource.
                'Ocp-Apim-Subscription-Region': self.location,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }

            # You can pass more than one object in body.
            body = [{
                'text': text
            }]

            # Translate the text
            request = requests.post(self.constructed_url, params=params, headers=headers, json=body)
            response = request.json()
            detected = response[0].get("detectedLanguage")
            translation = response[0].get("translations")[0]
            return {"detected_lang": detected['language'], 'detected_conf': detected['score'], 'trans_text': translation['text'].lower(),
                    'trans_lang': translation['to'], "error": ""}
        except Exception as exc:
            return {"error": str(exc)}
