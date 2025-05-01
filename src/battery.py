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

        device = '/org/bluez/hci0/dev_40_35_E6_16_8F_11'
        battery = 'org.bluez.Battery1'
        name = 'org.bluez.Device1'

        battery_life = devices[device][battery]['Percentage']
        device_name = devices[device][name]['Name']

        device_info = {
            'battery_life': battery_life,
            'device_name': device_name
        }

        return device_info

    except Exception as e:
        print(f'Dispositivo não encontrado {e}')
        return False


if __name__ == '__main__':
    battery = get_battery_level()
    print(battery)
