#5 обновление посвященно Павлу
import socketio
import eventlet
import random

sio = socketio.Server(cors_allowed_origins='*')

player_list = {}
admin_sid = None
role10 = 6 * ['Мирный житель'] + 2 * ['Мафия'] + ['Шериф'] + ['Дон мафии']
role8 = 5 * ['Мирный житель'] + 1 * ['Мафия'] + ['Шериф'] + ['Дон мафии']
role = role8
maf_targets = []
maf_target = None


@sio.event
def connect(sid, environ):
    print('Подключен клиент:', sid)
    resp = {'type': 'player_list', 'data': player_list}
    sio.emit('chat_message', resp, room=sid)



@sio.event
def disconnect(sid):
    print('Клиент отключен:', sid)
    # Удаляем соединение из комнаты
    sio.leave_room(sid, 'room')


@sio.event
def message(sid, data):
    global player_list, admin_sid

    print('Сообщение message от клиента {}: {}'.format(sid, data))
    # when nickname entering
    if len(data) == 1 and 'username' in data and isinstance(data['username'], str) and len(player_list) < 10:
        player_list[sid] = data
        player_list[sid]['admin'] = 'false'
        if admin_sid is None:  # first entered - admin
            admin_sid = sid
            player_list[sid]['admin'] = 'true'

        resp = {'type': 'joined_list', 'data': player_list}
        sio.enter_room(sid, room='room')
        sio.emit('chat_message', {'type': 'user_data', 'sid': sid, 'admin': player_list[sid]['admin']}, room=sid)
        sio.emit('chat_message', resp, room='room')
    # if player count already 10
    if len(data) == 1 and 'username' in data and isinstance(data['username'], str) and len(player_list) == 10:
        sio.emit('chat_message', 'player_list_is_full', room='room')

@sio.event
def start(sid, data):
    print('Сообщение start от клиента {}: {}'.format(sid, data))
    global player_list, role

    if data == 'start':
        # shuffle order of players
        keys = list(player_list.keys())
        random.shuffle(keys)
        shuffled_player_list = {}
        for num, key in enumerate(keys, start=1):
            player = player_list[key]
            player['number'] = num
            shuffled_player_list[key] = player
        # choose 8 players or 10
        if len(shuffled_player_list) <= 8:
            role = role8
            random.shuffle(role)
        elif len(shuffled_player_list) == 10:
            role = role10
            random.shuffle(role)
        # giving roles to players
        for sid, data in shuffled_player_list.items():
            data['role'] = role.pop()
            data.update({'status': 'alive'})
            data.update({'admin': 'false'})
        shuffled_player_list[admin_sid]['admin'] = 'true'
        player_list = shuffled_player_list
        resp = {'type': 'users_data', 'data': shuffled_player_list}
        # sending data to client
        sio.emit('chat_message', resp, room='room')

@sio.event
def kill(sid, data):
    print('Сообщение kill от клиента {}: {}'.format(sid, data))
    global player_list, maf_targets, maf_target

    if len(player_list) <= 8:
        maf_count = 2
    elif len(player_list) == 10:
        maf_count = 3

    print('len = ', len(player_list))
    print('maf_count = ', maf_count)
    print('maf_targets do = ', maf_targets)
    if len(maf_targets) < maf_count:  # waiting for all shots
        maf_targets.append(data)
        print('maf_targets posle = ', maf_targets)
    if len(maf_targets) == maf_count:  # when shot count is equal to mafia count
        if all(x == maf_targets[0] for x in maf_targets):  # if shots are same
            if maf_targets[0] != 0:
                maf_target = maf_targets[0]
            else:
                maf_target = '0'
        else:
            maf_target = '0'
    if maf_target is not None:  # send maf_target if it is not None
        sio.emit('chat_message', {"killed_player": maf_target}, room='room')
        # reset
        maf_count = 2
        maf_targets = []
        maf_target = None


# Запускаем сервер Socket.IO
if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
