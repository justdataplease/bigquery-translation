import json

import functions_framework
from translation import Translator


@functions_framework.http
def translate(request):
    """
    Defines translate Google Cloud Function
    :param request:
    :return:
    """
    request_json = request.get_json()
    calls = request_json['calls']
    replies = []
    trans = Translator()
    for call in calls:
        text = call[0]
        to_language = call[1]
        rs = trans.translate_text(text=text, to_language=to_language)
        # each reply is a STRING (JSON not currently supported)
        replies.append(json.dumps(rs, ensure_ascii=False))

    return json.dumps({'replies': replies})
