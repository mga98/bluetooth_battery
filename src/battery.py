from pydbus import SystemBus


def get_battery_level() -> dict:
    """
    Retorna informações do dispositivo bluetooth conectado

    :returns device_info: Dicionário com informações do dispositivo
    """
    try:
        bus = SystemBus()
        manager = bus.get('org.bluez', '/')
        devices = manager.GetManagedObjects()

        device_info = {}

        for value in devices.values():
            if value.get('org.bluez.Battery1'):
                for v in value.values():
                    if v.get('Name'):
                        battery = value.get('org.bluez.Battery1')
                        device_info['battery_life'] = battery['Percentage']
                        device_info['device_name'] = v['Name']
                        device_info['icon'] = f'{v['Icon']}-symbolic'

                        break

        return device_info

    except Exception as e:
        print(f'Dispositivo não encontrado {e}')
        return False


if __name__ == '__main__':
    battery = get_battery_level()
    print(battery)
