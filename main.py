import socketio
import eventlet
import random

sio = socketio.Server()

player_list = {}
role = 6 * ['Мирный житель'] + 2 * ['Мафия'] + ['Шериф'] + ['Дон мафии']


@sio.event
def connect(sid, environ):
    print('Подключен клиент:', sid)
    sio.emit('hello', 'Hello, world!', room=sid)



@sio.event
def disconnect(sid):
    print('Клиент отключен:', sid)
    # Удаляем соединение из комнаты
    sio.leave_room(sid, 'room')


@sio.event
def message(sid, data):

    print('Сообщение от клиента {}: {}'.format(sid, data))
    if len(data) == 1 and 'username' in data and isinstance(data['username'], str) and len(player_list) < 10:
        player_list[sid] = data
        sio.enter_room(sid, room='room')
        sio.emit('chat_message', player_list, room='room')
    if len(data) == 1 and 'username' in data and isinstance(data['username'], str) and len(player_list) == 10:
        sio.emit('chat_message', 'player_list_is_full', room='room')
    if data == 'start':
        keys = list(player_list.keys())
        random.shuffle(keys)
        shuffled_player_list = {}
        for num, key in enumerate(keys, start=1):
            player = player_list[key]
            player['number'] = num
            shuffled_player_list[key] = player
        random.shuffle(role)
        for sid, data in shuffled_player_list.items():
            data['role'] = role.pop()
            data.update({'status': 'alive'})
        sio.emit('chat_message', shuffled_player_list, room='room')







# Запускаем сервер Socket.IO
if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
