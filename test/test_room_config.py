
import requests



def test_room_config():
    url = "http://tg-proxy.coinpaas.com/room/config/load"
    body = {
        "mode":"test",
        "api_exrt:":{
            "room_name": "test",
        }
    }
    res = requests.post(url, json=body)
    print(res.json())

if __name__ == "__main__":
    test_room_config()
