import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UbicacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("ubicaciones", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("ubicaciones", self.channel_name)

    async def ubicacion_update(self, event):
        await self.send(text_data=json.dumps(event['data']))