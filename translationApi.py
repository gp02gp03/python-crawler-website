import os
from google.cloud import translate_v2

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\user\Desktop\python-crawler\translate.json"
translate_client = translate_v2.Client()

text = "02AZD880D U-WAVE-T 送信側 ブザータイプ (ミツトヨ)"
target = 'zh-TW'
output = translate_client.translate(text, target_language=target)

print(output['translatedText'])