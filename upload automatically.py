import urllib.request
import requests
import hashlib
import base64
import sys
import json
import time
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
timer = time.perf_counter
import zhconv                       # 如果要转换成繁体，需要pip install zhconv
import sys
import os


def google(file):
    api_url = "https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    audiofile = open(file, 'rb')
    audio_b64 = base64.b64encode(audiofile.read())
    audio_b64str = audio_b64.decode()
    voice = {
        "config":
            {
                # "encoding": "WAV",
                "languageCode": "yue-Hant-HK"
            },

        "audio":
            {
                "content": audio_b64str
            }
    }
    # 将字典格式的voice编码为utf8
    voice = json.dumps(voice).encode('utf8')

    req = urllib.request.Request(api_url, data=voice, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    response_str = response.read().decode('utf8')
    # ④
    # print(response_str)
    response_dic = json.loads(response_str)
    transcript = response_dic['results'][0]['alternatives'][0]['transcript']
    confidence = response_dic['results'][0]['alternatives'][0]['confidence']
    return transcript

# Iflytek
def getHeader(aue, engineType):
    APPID = "xxxxxxxx"
    API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    curTime = str(int(time.time()))
    param = "{\"aue\":\"" + aue + "\"" + ",\"engine_type\":\"" + engineType + "\"}"
    print("param:{}".format(param))
    paramBase64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')
    print("x_param:{}".format(paramBase64))

    m2 = hashlib.md5()
    m2.update((API_KEY + curTime + paramBase64).encode('utf-8'))
    checkSum = m2.hexdigest()
    print('checkSum:{}'.format(checkSum))
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    print(header)
    return header

def Iflytek(file_read):
    URL = "http://api.xfyun.cn/v1/service/v1/iat"
    aue = "raw"
    engineType = "sms16k"
    audio_iflytek = open(file_read, 'rb')
    data = {'audio': base64.b64encode(audio_iflytek.read())}
    r = requests.post(URL, headers=getHeader(aue, engineType), data=data)
    text_iflytek = (r.content.decode('utf-8'))
    response_iflytek = json.loads(text_iflytek)
    transcript_iflytek = response_iflytek['data']
    return transcript_iflytek


# Baidu
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
RATE = 16000;  # 固定值
IS_PY3 = sys.version_info.major == 3
API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
DEV_PID = 1637;  # 1637是粤语，1537是普通话
CUID = '123456PYTHON';
ASR_URL = 'http://vop.baidu.com/server_api'

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    # print(result_str)
    result = json.loads(result_str)
    # print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


rootdir = 'D:\HKDT_wav'
list = os.listdir(rootdir)
for i in range(0,len(list)):
  path = os.path.join(rootdir, list[i])
  if os.path.isfile(path):
      token = fetch_token()
      audio_file_Baidu = open(path, 'rb')
      FORMAT = audio_file_Baidu.name[-3:]
      speech_data = audio_file_Baidu.read()
      length = len(speech_data)
      params = {'cuid': CUID, 'token': token, 'dev_pid': DEV_PID}
      params_query = urlencode(params);

      headers = {
          'Content-Type': 'audio/' + FORMAT + '; rate=' + str(RATE),
          'Content-Length': length
      }
      req = Request(ASR_URL + "?" + params_query, speech_data, headers)
      try:
          begin = timer()
          f = urlopen(req)
          result_str = f.read()
          print("Request time cost %f" % (timer() - begin))
      except  URLError as err:
          print('asr http response http code : ' + str(err.code))
          result_str = err.read()
      data1 = json.loads(result_str.decode('utf-8'))

      transcript_iflytek = Iflytek(path)
      result_Google = google(path)
      transcript_Baidu = data1['result'][0]
      transformation_Baidu = zhconv.convert(transcript_Baidu, 'zh-hk')
      print(transcript_iflytek)      # 讯飞免费账户暂不支持粤语识别，所以这里是普通话识别结果
      print(result_Google)
      print(transcript_Baidu)
      print(transformation_Baidu)
      I = open(str(i)+"_iflytek.txt",'w')
      I.write(transcript_iflytek)
      f = open(str(i)+"_google.txt",'w')
      f.write(result_Google)
      f.close
      b = open(str(i) + "_Baidu.txt", 'w')
      b.write(transcript_Baidu)
      f.close
      i= i+1

   
