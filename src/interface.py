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
        self.devices_state = dict()

        # Botão de sair
        quit_item = Gtk.MenuItem(label='Sair')
        quit_item.connect('activate', self.quit)
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        # Ícone do sistema (removido vazio)
        # self.indicator.set_icon('')  # Defina um ícone se quiser

        # Thread de atualização
        self.running = True
        self.update_thread = threading.Thread(
            target=self.update_battery_loop,
            daemon=True
        )
        self.update_thread.start()

    def clear_menu(self) -> None:
        """
        Remove os itens de dispositivos do menu (mantém apenas o botão 'Sair')
        """
        for item in self.menu.get_children():
            if item.get_label() and item.get_label() != 'Sair':
                self.menu.remove(item)

    def look_for_devices_updates(self, devices_list: list) -> int:
        """
        Verifica mudanças no estado dos dispositivos (conexão ou novos)
        """
        devices_to_update = 0

        for device in devices_list:
            device_name = device['device_name']
            is_connected = device['connected']

            # Mudança no estado de conexão
            if device_name in self.devices_state:
                device_state = self.devices_state[device_name['connected']]

                if is_connected != device_state:
                    devices_to_update += 1
            else:
                # Novo dispositivo
                devices_to_update += 1

        return devices_to_update

    def update_devices_menu(self) -> None:
        """
        Atualiza o menu de dispositivos, se necessário
        """
        devices_list = get_battery_level()

        if self.look_for_devices_updates(devices_list) > 0:
            self.clear_menu()

            for device in devices_list:
                device_name = device['device_name']
                battery_life = device['battery_life']
                is_connected = device['connected']

                if battery_life:
                    label = f'{device_name}: {battery_life}%'
                else:
                    label = device_name

                device_item = Gtk.MenuItem(label=label)
                device_item.set_sensitive(is_connected)

                self.menu.prepend(device_item)

                # Atualiza estado
                self.devices_state[device_name] = {
                    'connected': is_connected
                }

            self.menu.show_all()

    def update_battery_loop(self) -> None:
        """
        Loop que atualiza o menu a cada 5 segundos
        """
        try:
            while self.running:
                if self.running:
                    GLib.idle_add(self.update_devices_menu)
                time.sleep(5)

        except Exception:
            logging.exception('Erro ao encontrar dispositivos')
            self.quit()

    def quit(self, _) -> None:
        """
        Encerra a aplicação de forma limpa
        """
        self.running = False
        self.update_thread.join()
        Gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    BatteryIndicator()
    Gtk.main()


if __name__ == '__main__':
    main()
