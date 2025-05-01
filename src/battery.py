from pydbus import SystemBus


def get_battery_level() -> int:
    """
    Retorna a bateria do dispositivo bluetooth conectado

    :returns battery_life: Nível da bateria (porcentagem)
    """
    try:
        bus = SystemBus()
        manager = bus.get('org.bluez', '/')
        devices = manager.GetManagedObjects()

        device = '/org/bluez/hci0/dev_40_35_E6_16_8F_11'
        battery = 'org.bluez.Battery1'

        battery_life = devices[device][battery]['Percentage']

        return battery_life

    except Exception as e:
        print(f'Dispositivo não encontrado {e}')
        return False
