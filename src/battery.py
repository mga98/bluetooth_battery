from pydbus import SystemBus


def get_battery_level():
    bus = SystemBus()
    manager = bus.get('org.bluez', '/')
    devices = manager.GetManagedObjects()

    device = '/org/bluez/hci0/dev_40_35_E6_16_8F_11'
    battery = 'org.bluez.Battery1'

    battery_life = devices[device][battery]['Percentage']

    return battery_life
