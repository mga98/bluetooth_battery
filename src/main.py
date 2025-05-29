import gi
import time
import signal
import threading

from battery import get_battery_level, list_devices

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import AppIndicator3, Gtk, GLib  # noqa


class BatteryIndicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            'bt_battery',
            '',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.pairable_devices = list()

        self.battery_item = Gtk.MenuItem(label='Bateria do dispositivo: ...%')
        self.menu.append(self.battery_item)

        self.menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label='Sair')
        quit_item.connect('activate', self.quit)
        self.menu.append(quit_item)
        self.menu.show_all()

        self.indicator.set_menu(self.menu)

        # Thread para atualizar a bateria
        self.running = True
        self.update_thread = threading.Thread(
            target=self.update_battery_loop,
            daemon=True
        )
        self.update_thread.start()

    def update_pairable_devices(self) -> int:
        """
        Atualiza a lista de dispositivos disponíveis para conexão
        e retorna a quantidade de dispositivos que foram atualizados

        :returns devices_to_update: Quantidade de dispositivos que foram
            atualizados em self.paraible_devices
        """
        devices_to_update = 0
        for device in list_devices():
            if device not in self.pairable_devices:
                self.pairable_devices.append(device)
                devices_to_update += 1

        return devices_to_update

    def update_devices_menu(self) -> None:
        """
        Atualiza o menu de dispositivos disponíveis para conexão caso
        haja algum novo dispositivo disponível
        """
        for device in self.pairable_devices:
            device_item = Gtk.MenuItem(label=device)
            device_item.set_sensitive(False)
            menu_labels = [label.get_label() for label in self.menu]

            # Só adiciona se o dispositivo ainda não estiver no menu
            if device_item.get_label() not in menu_labels:
                # Insere os itens na posição [1] da lista para garantir
                # que o botão de sair apareça no fim
                self.menu.insert(device_item, 1)

            self.menu.show_all()

    def update_battery_loop(self) -> None:
        '''
        Faz o update da interface gráfica para atualizar o nível
        da bateria a cada 5 segundos
        '''
        try:
            while self.running:
                device = get_battery_level()
                devices_to_update = self.update_pairable_devices()

                # Só atualiza o menu se devices_to_update for maior do
                # que 0 (evitando updates desnecessários)
                if devices_to_update > 0:
                    GLib.idle_add(self.update_devices_menu)

                if device:
                    GLib.idle_add(
                        self.indicator.set_icon,
                        device['icon']
                    )
                    GLib.idle_add(
                        self.battery_item.set_label,
                        f'{device['device_name']}: {device['battery_life']}%'
                    )
                    GLib.idle_add(
                        self.indicator.set_label,
                        f'{device['battery_life']}%', ''
                    )

                else:
                    GLib.idle_add(
                        self.indicator.set_icon,
                        ''
                    )
                    GLib.idle_add(
                        self.battery_item.set_label,
                        'Dispositivo não encontrado'
                    )
                    GLib.idle_add(
                        self.indicator.set_label,
                        '', ''
                    )

                time.sleep(5)

        except Exception as e:
            print(f'Erro ao carregar informações do dispositivo: {e}')
            self.quit()

    def quit(self, _) -> None:
        self.running = False
        Gtk.main_quit()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    BatteryIndicator()
    Gtk.main()


if __name__ == '__main__':
    main()
