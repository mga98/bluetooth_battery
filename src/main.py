import gi
import time
import signal
import threading

from battery import get_battery_level

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import AppIndicator3, Gtk, GLib  # noqa


class BatteryIndicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "bt_battery",
            "audio-headphones-symbolic",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.battery_item = Gtk.MenuItem(label="Bateria do fone: ...%")
        self.battery_item.set_sensitive(False)

        self.menu.append(self.battery_item)

        self.menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label="Sair")
        quit_item.connect("activate", self.quit)
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

    def update_battery_loop(self) -> None:
        """
        Faz o update da interface gráfica para atualizar o nível
        da bateria a cada 5 segundos
        """
        while self.running:
            device = get_battery_level()

            if device:
                GLib.idle_add(
                    self.battery_item.set_label,
                    f"{device['device_name']}: {device['battery_life']}%"
                )
            else:
                GLib.idle_add(
                    self.battery_item.set_label,
                    "Fone não encontrado"
                )

            time.sleep(5)

    def quit(self, _) -> None:
        self.running = False
        Gtk.main_quit()


def main():
    # permite Ctrl+C no terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    BatteryIndicator()
    Gtk.main()


if __name__ == "__main__":
    main()
