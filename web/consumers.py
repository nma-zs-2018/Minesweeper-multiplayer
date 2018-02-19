from channels.consumer import SyncConsumer
import json

"""
conn = set()
last = {}


def first():
    global last
    if SliderValues.objects.count() < 1:
        SliderValues().save()
    val = SliderValues.objects.all()[0]
    last['slider1'] = val.slider1
    last['slider2'] = val.slider2
    last['text'] = val.text

first()

class EchoConsumer(SyncConsumer):
    def websocket_connect(self, event):
        conn.add(self)
        self.send({
            "type": "websocket.accept",
        })
        for key, value in last.items():
            self.send({
                "type": "websocket.send",
                "text": "{\"who\": \"" + key + "\", \"data\": \"" + str(value) + "\"}",
            })

    def websocket_receive(self, event):
        global last
        x = json.loads(event['text'])
        last[x['who']] = x['data']
        a = {
                "type": "websocket.send",
                "text": "{\"who\": \"" + x['who'] + "\", \"data\": \"" + x['data'] + "\"}",
            }
        for s in conn:
            s.send(a)

    def websocket_disconnect(self, event):
        conn.remove(self)
        if len(conn) == 0:
            global last
            val = SliderValues.objects.all()[0]
            val.slider1 = last['slider1']
            val.slider2 = last['slider2']
            val.text = last['text']
            val.save()

"""