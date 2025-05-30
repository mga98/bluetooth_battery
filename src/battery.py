from pydbus import SystemBus


def get_all_devices() -> dict:
    """
    Retorna as informações de todos os dipositivos blueetooth disponíveis

    :returns devices: Dicionário com informações dos dispositivos bluetooth
        disponiveis
    """
    try:
        bus = SystemBus()
        manager = bus.get('org.bluez', '/')
        devices = manager.GetManagedObjects()

        return devices

    except Exception as e:
        return {'Error': f'Erro ao encontrar dispositivos: {e}'}


def list_devices() -> list:
    """
    Lista todos os dispositivos bluetooth disponíveis

    :returns devices_list: Lista com todos os dispositivos
        disponiveis
    """
    try:
        devices = get_all_devices()
        devices_list = []

        for value in devices.values():
            for v in value.values():
                if v.get('Name') and v.get('Pairable') is not False:
                    devices_list.append(v['Name'])

        return devices_list

    except Exception as e:
        return {'Error': f'Erro ao listar dispositivos: {e}'}


def get_battery_level() -> dict:
    """
    Retorna informações do dispositivo bluetooth conectado

    :returns device_info: Dicionário com informações do dispositivo
    """
    try:
        devices = get_all_devices()
        device_info = []

        for value in devices.values():
            for v in value.values():
                if v.get('Name') and v.get('Paired') is True:
                    try:
                        battery_life = value.get(
                            'org.bluez.Battery1'
                        )['Percentage']
                    except Exception:
                        battery_life = None

                    device_info.append({
                        'battery_life': battery_life,
                        'device_name': v['Name'],
                        'connected': v['Connected'],
                        'icon': f'{v['Icon']}-symbolic'
                    })

        return device_info

    except Exception as e:
        print(f'Dispositivo não encontrado {e}')
        return False


if __name__ == '__main__':
    import json  # noqa
    battery = get_battery_level()
    print(json.dumps(battery, indent=2))

    # devices = get_all_devices()
    # print(json.dumps(devices, indent=2))

    # devices_list = list_devices()
    # print(devices_list)
