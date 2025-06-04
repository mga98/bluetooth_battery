import gi
import time
import signal
import threading
import logging

from battery import get_battery_level

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import AppIndicator3, Gtk, GLib  # noqa

logging.basicConfig(level=logging.INFO)


class BatteryIndicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            'bt_battery',
            '',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.devices_state = {}
        self.menu_items = {}

        quit_item = Gtk.MenuItem(label='Sair')
        quit_item.connect('activate', self.quit)
        self.quit_item = quit_item

        self.indicator.set_menu(self.menu)

        self.running = True
        self.update_thread = threading.Thread(
            target=self.update_battery_loop,
            daemon=True
        )
        self.update_thread.start()

    def format_device_label(self, name, battery):
        return f"{name}: {battery}%" if battery else name

    def update_devices_menu(self) -> None:
        devices_list = get_battery_level()
        devices_list.sort(key=lambda d: d['device_name'].lower())

        current_device_names = {
            device['device_name'] for device in devices_list
        }
        known_device_names = set(self.menu_items.keys())

        first_connected_device = None

        for device in devices_list:
            name = device['device_name']
            connected = device['connected']
            battery = device['battery_life']
            icon = device['icon']
            label = self.format_device_label(name, battery)

            if connected and not first_connected_device:
                first_connected_device = device

            if name in self.menu_items:
                menu_item = self.menu_items[name]

                if menu_item.get_label() != label:
                    menu_item.set_label(label)

                menu_item.set_sensitive(connected)

            else:
                menu_item = Gtk.MenuItem(label=label)
                menu_item.device_name = name

                menu_item.connect('activate', self.get_icon)
                menu_item.set_sensitive(connected)

                self.menu.append(menu_item)
                self.menu_items[name] = menu_item

                menu_item.show()

            print(self.menu_items)
            self.devices_state[name] = {
                'connected': connected,
                'icon': icon,
                'battery': battery
            }

        # Adiciona o botão de sair
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(self.quit_item)

        removed_devices = known_device_names - current_device_names
        for name in removed_devices:
            item = self.menu_items.pop(name)
            self.menu.remove(item)
            self.devices_state.pop(name, None)

        if first_connected_device:
            self.indicator.set_icon(first_connected_device['icon'])
            self.indicator.set_label(
                f"{first_connected_device['battery_life']}%", ''
            )

        self.menu.show_all()

    def update_battery_loop(self) -> None:
        try:
            while self.running:
                if self.running:
                    GLib.idle_add(self.update_devices_menu)
                time.sleep(5)

        except Exception:
            logging.exception('Erro ao encontrar dispositivos')
            self.quit()

    def get_icon(self, item) -> None:
        device = getattr(item, 'device_name', None)

        if device and device in self.devices_state:
            icon = self.devices_state[device]['icon']
            battery = self.devices_state[device]['battery']
            self.indicator.set_icon(icon)
            self.indicator.set_label(f'{battery}%', '')

        else:
            logging.warning(
                'Dispositivo não encontrado ao tentar definir o ícone.'
            )

    def quit(self, _) -> None:
        self.running = False
        self.update_thread.join()
        Gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    BatteryIndicator()
    Gtk.main()


if __name__ == '__main__':
    main()
