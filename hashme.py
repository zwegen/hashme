import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import os
import subprocess
import hashlib
import threading

class HashComparer(Gtk.Window):
    def __init__(self):
        super().__init__(title="HashMe")
        self.set_default_size(580, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Set window icon
        self.set_icon_from_file("/usr/share/icons/hashme.png")

        # Layout for the main window
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_bottom(10)
        self.add(vbox)

        # First file selection button
        self.file_button1 = Gtk.Button(label="Select file")
        self.file_button1.connect("clicked", self.on_file_button1_clicked)
        vbox.pack_start(self.file_button1, False, False, 0)

        # Second file selection button
        self.file_button2 = Gtk.Button(label="Select file")
        self.file_button2.connect("clicked", self.on_file_button2_clicked)
        vbox.pack_start(self.file_button2, False, False, 0)

        # Manual SHA-256 input field
        self.manual_hash_entry1 = Gtk.Entry()
        self.manual_hash_entry1.set_alignment(0.5)
        self.manual_hash_entry1.set_placeholder_text("Enter hash value")
        vbox.pack_start(self.manual_hash_entry1, False, False, 0)

        # Frame for comparison result
        self.comparison_result_frame = Gtk.Frame()
        self.comparison_result_frame.set_label("Result")
        self.comparison_result_label = Gtk.Label(label="")
        self.comparison_result_frame.add(self.comparison_result_label)
        self.comparison_result_frame.set_size_request(-1, 90)
        vbox.pack_start(self.comparison_result_frame, False, False, 0)

        # Spinner for calculation
        self.spinner = Gtk.Spinner()
        vbox.pack_start(self.spinner, False, False, 0)

        # Horizontal box for compare and reset buttons
        hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_buttons, False, False, 0)

        # Compare button
        self.compare_button = Gtk.Button(label="Compare")
        self.compare_button.connect("clicked", self.on_compare_button_clicked)
        self.compare_button.set_size_request(-1, 30)
        compare_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON)
        self.compare_button.set_image(compare_icon)
        hbox_buttons.pack_start(self.compare_button, True, True, 0)

        # Reset button
        self.reset_button = Gtk.Button()
        reset_icon = Gtk.Image.new_from_icon_name("reload", Gtk.IconSize.BUTTON)
        self.reset_button.add(reset_icon)
        self.reset_button.connect("clicked", self.on_reset_button_clicked)
        self.reset_button.set_size_request(30, 30)
        hbox_buttons.pack_start(self.reset_button, False, False, 0)

        # Save button
        self.save_button = Gtk.Button()
        save_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON)
        self.save_button.add(save_icon)
        self.save_button.connect("clicked", self.on_save_button_clicked)
        self.save_button.set_size_request(30, 30)
        hbox_buttons.pack_start(self.save_button, False, False, 0)

        # Info button (with standard info icon)
        self.info_button = Gtk.Button()
        info_icon = Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.BUTTON)  # Standard info icon
        self.info_button.add(info_icon)
        self.info_button.connect("clicked", self.on_info_button_clicked)
        self.info_button.set_size_request(30, 30)
        hbox_buttons.pack_start(self.info_button, False, False, 0)

    def get_desktop_path(self):
        try:
            desktop_path = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip()
            if os.path.exists(desktop_path):
                return desktop_path
        except subprocess.CalledProcessError:
            pass
        
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        if os.path.exists(desktop_path):
            return desktop_path

        return None

    def on_file_button1_clicked(self, widget):
        self.file_path1 = self.select_file()
        if self.file_path1:
            threading.Thread(target=self.calculate_and_update, args=(self.file_path1, self.file_button1)).start()

    def on_file_button2_clicked(self, widget):
        self.file_path2 = self.select_file()
        if self.file_path2:
            threading.Thread(target=self.calculate_and_update, args=(self.file_path2, self.file_button2)).start()

    def select_file(self):
        dialog = Gtk.FileChooserDialog(
            title="Please select a file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            return file_path
        dialog.destroy()
        return None

    def calculate_and_update(self, file_path, button):
        # Start spinner
        GLib.idle_add(self.spinner.start)

        file_hash = self.calculate_sha256(file_path)

        # Stop spinner and update button
        GLib.idle_add(self.spinner.stop)
        GLib.idle_add(button.set_label, file_hash)

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.comparison_result_label.set_markup(f'<span color="red" size="large">Error reading file: {e}</span>')
            return ""

    def on_compare_button_clicked(self, widget):
        self.compare_hashes()

    def compare_hashes(self):
        manual_hash1 = self.manual_hash_entry1.get_text().strip()

        if hasattr(self, 'file_path1') and manual_hash1:
            file_hash1 = self.calculate_sha256(self.file_path1)
            self.compare_and_display(file_hash1, manual_hash1)
        elif hasattr(self, 'file_path2') and manual_hash1:
            file_hash2 = self.calculate_sha256(self.file_path2)
            self.compare_and_display(file_hash2, manual_hash1)
        elif hasattr(self, 'file_path1') and hasattr(self, 'file_path2'):
            file_hash1 = self.calculate_sha256(self.file_path1)
            file_hash2 = self.calculate_sha256(self.file_path2)
            self.compare_and_display(file_hash1, file_hash2)

    def compare_and_display(self, hash1, hash2):
        if hash1 == hash2:
            self.comparison_result_label.set_markup('<span color="green" size="large">Hash values match!</span>')
        else:
            self.comparison_result_label.set_markup('<span color="red" size="large">Hash values do NOT match!</span>')

    def on_reset_button_clicked(self, widget):
        """Reset all fields and stored values."""
        self.file_button1.set_label("Select file")
        self.file_button2.set_label("Select file")
        self.manual_hash_entry1.set_text("")
        self.comparison_result_label.set_markup("")
        
        if hasattr(self, 'file_path1'):
            del self.file_path1
        if hasattr(self, 'file_path2'):
            del self.file_path2

    def on_save_button_clicked(self, widget):
        desktop_path = self.get_desktop_path()
        if not desktop_path:
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Desktop directory not found!"
            )
            dialog.run()
            dialog.destroy()
            return

        file_path = os.path.join(desktop_path, "hashme_output.txt")
        
        file_hash1 = ""
        file_hash2 = ""
        if hasattr(self, 'file_path1'):
            file_hash1 = self.calculate_sha256(self.file_path1)
        if hasattr(self, 'file_path2'):
            file_hash2 = self.calculate_sha256(self.file_path2)

        manual_hash1 = self.manual_hash_entry1.get_text().strip()
        comparison_result = self.comparison_result_label.get_text()

        with open(file_path, 'w') as file:
            file.write(f"Summary\n\n")
            file.write(f"Hash File 1  :  {file_hash1}\n")
            file.write(f"Hash File 2  :  {file_hash2}\n")
            file.write(f"Manual Hash 1:  {manual_hash1}\n\n")
            file.write("Result       :  ")
            file.write(comparison_result)

        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f"Hash values saved: {file_path}"
        )
        dialog.run()
        dialog.destroy()

    def on_info_button_clicked(self, widget):
        # Create the info dialog without an icon
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.OTHER,  # Set message type to OTHER to remove the icon
            buttons=Gtk.ButtonsType.OK,
        )

        # Use GTK markup for the text
        info_text = """
<b>HashMe</b>\n
<i>With HashMe, you can calculate and compare SHA-256 hash values to verify the integrity of files.\n\nYou can select files or manually input a hash value to check if the hash values match.\n\nHashMe provides instant feedback.</i>\n
    """

        # Create and set the markup text in the dialog
        info_label = Gtk.Label()
        info_label.set_markup(info_text)

        # Enable text wrapping
        info_label.set_line_wrap(True)
        info_label.set_justify(Gtk.Justification.LEFT)

        # Add margin (padding) around the text
        info_label.set_margin_top(0)  # Top margin
        info_label.set_margin_bottom(0)  # Bottom margin
        info_label.set_margin_start(26)  # Left margin
        info_label.set_margin_end(26) # Right margin

        # Add the formatted text to the dialog
        scrolled_window = Gtk.ScrolledWindow()  # Scrollable window
        scrolled_window.add(info_label)  # Add label to the scrollable window

        # Add the scrollable window to the dialog
        dialog.vbox.pack_start(scrolled_window, True, True, 0)

        # Add a link button
        donate_button = Gtk.LinkButton(uri="https://coinos.io/Bitcoininfo")
        donate_button.set_label("Donate")
        dialog.vbox.pack_start(donate_button, False, False, 0)

        # Set a maximum width and minimum height for the dialog
        dialog.set_default_size(560, -1)  # 550px width, no fixed height
        dialog.set_size_request(-1, 400)  # Set minimum height of 250px

        # Adjust dialog size dynamically based on content
        dialog.set_resizable(True)

        # Show the dialog
        info_label.show()
        donate_button.show()
        scrolled_window.show()

        # Run the dialog
        dialog.run()
        dialog.destroy()

win = HashComparer()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

