import base64,requests
from config import HF_API_KEY

API_URL = "https://router.huggingface.co/v1/chat/completions"

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}

MODELS = [

"Qwen/Qwen3-VL-8B-Instruct:together",

"Qwen/Qwen3-VL-32B-Instruct:together",

"Qwen/Qwen2.5-VL-32B-Instruct:together",

"Qwen/Qwen2-VL-7B-Instruct:together",

]

def data_url(b:bytes)->str:
    return "data:image/jpeg;base64," + base64.b64encode(b).decode("utf-8")


def extract_error(r:requests.Response)->str:
    try:
        j=r.json()
        return j.get('error',{}).get('message') or str(j)
    except Exception:
        return r.reason or 'Request Failed!'


def box(title:str,lines:list[str],icon:str):
    w=max(30,len(title)+4,*(len(x) for x in lines))
    print("\n" + "┏" + "━" * (w + 2) + "┓")
    print(f"┃{icon} {title.ljust(w - 2)}┃")
    print("┣" + "━" * (w + 2) + "┫")
    for x in lines:
        print(f"┃ {x.ljust(w)} ┃")
    print("┗" + "━" * (w + 2) + "┛\n")

def caption_single():
    image_source=input('Enter image file name:\n')
    try:
        with open(image_source,'rb') as f:
            img=f.read()
    except Exception:
        box('FILE ERROR',['There is a file error!','Make sure path is correct!'],':-(')
        caption_single()
    base={
        'messages':[{
            'role':'user','content':[
                {'type':'text','text':'Give a short caption for this image.'},
                {'type':'image_url','image_url':{'url':data_url(img)}}
            ],
        }],
        'max_tokens':60,
        'temperature':0.2
    }
    last=None
    for model in MODELS:
        payload=dict(base,model=model)
        r=requests.post(API_URL,headers=HEADERS,json=payload,timeout=120)
        d=r.json()
        cap=(d.get('choices',[{}])[0].get('message',{}).get('content') or '')
        if cap:
            box('IMAGE CAPTION GENERATED!',[
                f'Image:{image_source}','Caption:',f'{cap}'
            ],':-)')
            return
        last='No caption found'
    box('Caption Failed',[f'Image:{image_source}',f'ERROR : {last or 'Unknown Error'}'],':-(')
    redo=input('Do you want to check another picture? (y/n)')
    if redo == 'y' or redo=='yes':
        caption_single()
    else:
        print('BYE!')
        exit()
caption_single()