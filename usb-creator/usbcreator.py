#!/usr/bin/env python3


# Make sure the right Gtk version is loaded
import gi
gi.require_version('Gtk', '3.0')

# from gi.repository import Gtk, GdkPixbuf, GObject, Pango, Gdk, GLib
from gi.repository import Gtk, GLib
from os.path import join, abspath, dirname, basename, islink, \
                    splitext, exists, expanduser, isdir, getsize
import os
import re
from glob import glob
from datetime import datetime
from queue import Queue

# Local imports
from .utils import ExecuteThreadedCommands, getoutput, \
                              shell_exec, getPackageVersion, get_user_home, \
                              get_fuzzy_ratio
from .dialogs import MessageDialog, ErrorDialog, WarningDialog, \
                                   SelectFileDialog, QuestionDialog
from .combobox import ComboBoxHandler
from .treeview import TreeViewHandler
from .logger import Logger
from .udisks2 import Udisks2

# i18n: http://docs.python.org/3/library/gettext.html
import gettext
_ = gettext.translation('usb-creator', fallback=True).gettext

#class for the main window
class USBCreator(object):

    def __init__(self, debug=False):
        self.debug = debug

        # Load window and widgets
        self.scriptName = basename(__file__)
        self.scriptDir = abspath(dirname(__file__))
        self.mediaDir = '/usr/share/usb-creator'
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(self.mediaDir, 'usb-creator.glade'))

        # Main window objects
        go = self.builder.get_object
        self.window = go("usb-creator")
        self.lblDevice = go("lblDevice")
        self.lblPartition = go("lblPartition")
        self.chkPartition = go("chkPartition")
        self.lblIso = go("lblIso")
        self.lblAvailable = go("lblAvailable")
        self.lblRequired = go("lblRequired")
        self.cmbDevice = go("cmbDevice")
        self.cmbDeviceHandler = ComboBoxHandler(self.cmbDevice)
        self.txtIso = go("txtIso")
        self.lblWriteSingle = go("lblWriteSingle")
        self.chkWriteSingle = go("chkWriteSingle")
        self.btnRefresh = go("btnRefresh")
        self.btnUnmount = go("btnUnmount")
        self.btnBrowseIso = go("btnBrowseIso")
        self.btnClear = go("btnClear")
        self.lblForceDistro = go("lblForceDistro")
        self.chkForceDistro = go("chkForceDistro")
        self.cmbDistros = go("cmbDistros")
        self.cmbDistrosHandler = ComboBoxHandler(self.cmbDistros)
        self.btnExecute = go("btnExecute")
        self.lblUsb = go("lblUsb")
        self.tvUsbIsos = go("tvUsbIsos")
        self.btnDelete = go("btnDelete")
        self.pbUsbCreator = go("pbUsbCreator")
        self.statusbar = go("statusbar")

        # Translations
        self.title = "USB Creator"
        self.window.set_title(self.title)
        self.lblDevice.set_label(_("Device"))
        self.lblPartition.set_label(_("Partition device"))
        self.lblPartition.set_tooltip_text(_("This will remove all data from the device."))
        self.lblUsb.set_label(_("USB"))
        self.available_text = _("Available")
        self.required_text = _("Required")
        self.btnExecute.set_label("_{}".format(_("Execute")))
        self.lblIso.set_label(_("ISO"))
        self.lblWriteSingle.set_label(_("Write single ISO"))
        self.lblWriteSingle.set_tooltip_text(_("Write a single ISO to USB using dd"))
        self.btnDelete.set_label("_{}".format(_("Remove")))
        self.btnRefresh.set_tooltip_text(_("Refresh device list"))
        self.btnUnmount.set_tooltip_text(_("Unmount device"))
        self.btnBrowseIso.set_tooltip_text(_("Browse for ISO file"))
        self.btnClear.set_tooltip_text(_("Clear the ISO field"))
        self.lblForceDistro.set_label(_("Manual"))
        self.lblForceDistro.set_tooltip_text(_("Manually select the distribution name if {title} cannot\n"
                                               "determine the distribution name automatically.".format(title=self.title)))

        # Log lines to show: check string, 0=pulse, 1=get percentage, show line (translatable)
        copy_string = _("Copy ISO to USB...")
        self.log_lines = []
        self.log_lines.append(["copied:", 1, copy_string])
        self.log_lines.append(["bytes (", 1, copy_string])
        self.log_lines.append(["prepare copy", 0, _("Prepare copy of ISO...")])
        self.log_lines.append(["verify hash", 0, _("Verify hash of ISO...")])
        self.log_lines.append(["install grub", 0, _("Install Grub...")])
        self.log_lines.append(["unpacking", 0, _("Unpacking ISO...")])
        self.log_lines.append(["gather iso", 0, _("Gather ISO information...")])

        # Initiate variables
        self.device = {}
        self.device['path'] = ''
        self.device['mount'] = ''
        self.device['size'] = 0
        self.device['available'] = 0
        self.device["new_iso"] = ''
        self.device["new_iso_required"] = 0
        self.logos = self.get_logos()
        self.queue = Queue(-1)
        self.threads = {}
        self.htmlDir = join(self.mediaDir, "html")
        self.helpFile = join(self.get_language_dir(), "help.html")
        log_dir = join(get_user_home(), '.usb-creator')
        if not exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = join(log_dir, 'usb-creator.log')
        self.log = Logger(self.log_file, addLogTime=False, maxSizeKB=0)
        self.tvUsbIsosHandler = TreeViewHandler(self.tvUsbIsos)
        self.udisks2 = Udisks2(debug=self.debug)

        self.lblAvailable.set_label('')
        self.lblRequired.set_label('')
        
        # Get distro names
        distros = getoutput('usb-creator -D')
        distros = sorted(distros[0].split())
        self.cmbDistrosHandler.fillComboBox(distros, 0)
        self.cmbDistros.set_sensitive(False)

        # Connect builder signals and show window
        self.builder.connect_signals(self)
        self.window.show_all()

        # Get attached devices
        self.refresh()

        # Init log
        init_log = ">>> Start USB Creator: {} <<<".format(datetime.now())
        self.log.write(init_log)

        # Version information
        self.version_text = _("Version")
        self.pck_version = getPackageVersion('usb-creator')
        self.set_statusbar_message("{}: {}".format(self.version_text, self.pck_version))

    # ===============================================
    # Main window functions
    # ===============================================

    def on_btnExecute_clicked(self, widget):
        if exists(self.device["path"]):
            iso = self.device["new_iso"]
            iso_path = self.txtIso.get_text().strip()

            # ISO path does not exist
            if iso != iso_path:
                msg = _("Cannot add ISO from path: {}.\n"
                        "Please, remove the ISO path or browse for an existing ISO.")
                WarningDialog(self.btnExecute.get_label().replace('_', ''), msg.format(iso_path))
                return True

            # Check if there is enough space
            available = self.device["available"]
            if (available) - self.device["new_iso_required"] < 0:
                msg = _("There is not enough space available on the pen drive.\n"
                        "Please, remove unneeded files before continuing.")
                WarningDialog(self.btnExecute.get_label().replace('_', ''), msg)
                return True
                
            # Check if user wants to force the distribution configuration
            options = ''
            if self.chkForceDistro.get_active():
                options = '-f {} '.format(self.cmbDistrosHandler.getValue())
            if self.chkPartition.get_active():
                options += '-p'
            if self.chkWriteSingle.get_active():
                options = '-u'

            cmd = 'usb-creator {options} "{iso}" {device}'.format(options=options, iso=iso, device=self.device["path"])
            self.log.clear()
            self.log.write("Execute command: {}".format(cmd))
            self.exec_command(cmd)

    def on_chkPartition_toggled(self, widget):
        if widget.get_active(): self.chkWriteSingle.set_active(False)

    def on_chkWriteSingle_toggled(self, widget):
        if widget.get_active(): self.chkPartition.set_active(False)
        self.on_cmbDevice_changed()

    def on_btnDelete_clicked(self, widget):
        selected_isos = self.tvUsbIsosHandler.getToggledValues(toggleColNr=0, valueColNr=2)
        if selected_isos:
            msg =  _("Are you sure you want to remove the selected ISO from the device?")
            answer = QuestionDialog(self.btnDelete.get_label().replace('_', ''), msg)
            if answer:
                for iso in selected_isos:
                    iso_path = join(self.device["mount"], iso)
                    if exists(iso_path):
                        self.log.write("Remove ISO: {}".format(iso_path))
                        shell_exec("usb-creator -r {iso} {device}".format(iso=iso_path, device=self.device["path"]))
                        self.refresh()
                        self.fill_treeview_usbcreator(self.device["mount"])

    def on_btnBrowseIso_clicked(self, widget):
        file_filter = Gtk.FileFilter()
        file_filter.set_name("ISO")
        file_filter.add_mime_type("application/x-cd-image")
        file_filter.add_pattern("*.iso")

        start_dir = dirname(self.txtIso.get_text().strip())
        if not exists(start_dir):
            start_dir = expanduser("~")

        iso = SelectFileDialog(title=_('Select ISO'), start_directory=start_dir, gtkFileFilter=file_filter).show()
        if iso is not None:
            self.log.write("Add ISO: {}".format(iso))
            self.txtIso.set_text(iso)

    def on_btnClear_clicked(self, widget):
        self.txtIso.set_text('')

    def on_txtIso_changed(self, widget=None):
        iso_path = self.txtIso.get_text().strip()
        if exists(iso_path):
            if isdir(iso_path):
                isos = glob(join(iso_path, '*.iso'))
                if isos:
                    required = 0
                    for iso in isos:
                        # Check if these ISOs overwrite current USB ISOs
                        check_usb_iso_size = 0
                        check_usb_iso = join(self.device["mount"], basename(iso))
                        if exists(check_usb_iso):
                            check_usb_iso_size = self.get_iso_size(check_usb_iso)
                        required += (self.get_iso_size(iso) - check_usb_iso_size)
                    if required < 0:
                        required = 0
                    self.lblRequired.set_label("{}: {} MB".format(self.required_text, int(required / 1024)))
                    # Save the info
                    self.device["new_iso"] = iso_path
                    self.device["new_iso_required"] = required
                    self.log.write("New ISO directory: {}, {}".format(iso_path, required))
                else:
                    self.device["new_iso"] = ''
                    self.device["new_iso_required"] = 0
                    self.log.write("New ISO directory does not contain ISOs: {}".format(iso_path))
            else:
                # Check if this ISO overwrites current USB ISO
                if self.chkWriteSingle.get_active():
                    required = self.get_iso_size(iso_path)
                else:
                    check_usb_iso_size = 0
                    check_usb_iso = join(self.device["mount"], basename(iso_path))
                    if exists(check_usb_iso):
                        check_usb_iso_size = self.get_iso_size(check_usb_iso)
                    required = (self.get_iso_size(iso_path) - check_usb_iso_size)
                self.lblRequired.set_label("{}: {} MB".format(self.required_text, int(required / 1024)))
                # Save the info
                self.device["new_iso"] = iso_path
                self.device["new_iso_required"] = required
                self.log.write("New ISO: {}, {}".format(iso_path, required))
        else:
            self.device["new_iso"] = ''
            self.device["new_iso_required"] = 0
            self.lblRequired.set_text('')

    def on_btnRefresh_clicked(self, widget=None):
        self.refresh()

    def on_btnUnmount_clicked(self, widget):
        unmount_text = _("Unmount")
        device = self.device["path"]
        try:
            self.udisks2.unmount_drive(device)
            self.refresh()
            msg = _("You can now safely remove the device.")
        except Exception as e:
            msg = _("Could not unmount the device.\n"
                    "Please unmount the device manually.")
            self.log.write("ERROR: %s" % str(e))
        MessageDialog(unmount_text, msg)

    def on_cmbDevice_changed(self, widget=None):
        drive_path = self.cmbDeviceHandler.getValue()
        device_paths = []
        if drive_path is not None:
            drive = self.udisks2.devices[drive_path]
            device_paths = self.udisks2.get_drive_device_paths(drive_path)
            device = ''
            mount = ''
            size = 0
            available = 0

            # Check the largest partition
            for dp in device_paths:
                dp_size = drive[dp]['total_size']
                if dp_size > size:
                    size = dp_size
                    available = drive[dp]['free_size']
                    device = dp
            
            if device:
                # USB has at least one partition
                mount = drive[device]['mount_point']
                if not exists(mount):
                    # Mount if not already mounted
                    try:
                        mount = self.udisks2.mount_device(device)
                    except Exception as e:
                        self.show_message(5)
                        self.log.write("ERROR: %s" % str(e))
                # Save size and available space
                size = drive[device]['total_size']
                available = drive[device]['free_size']
            else:
                msg = _("No partition found.\n"
                        "Please format the USB before you continue.")
                MessageDialog(_("No Partition"), msg)
                # Get free size of USB (in case of no partitions)
                size = drive['total_size']
                available = drive['free_size']

            self.fill_treeview_usbcreator(mount)
            if available == 0:
                available = drive['free_size']
            self.lblAvailable.set_label("{}: {} MB".format(self.available_text, int(available / 1024)))

            # Save the info
            self.device['path'] = drive_path
            self.device['mount'] = mount
            self.device['size'] = size
            self.device['available'] = available
            self.log.write("Selected device info: {}".format(self.device))

            # Update info
            iso_path = self.txtIso.get_text().strip()
            if iso_path != "" and exists(iso_path):
                self.on_txtIso_changed()
        else:
            self.fill_treeview_usbcreator()
            self.lblAvailable.set_label('')
            self.lblRequired.set_label('')
            self.txtIso.set_text('')
            self.device['path'] = ''
            self.device['mount'] = ''
            self.device['size'] = 0
            self.device['available'] = 0
            self.device["new_iso"] = ''
            self.device["new_iso_required"] = 0
            
    def on_chkForceDistro_toggled(self, widget):
        self.cmbDistros.set_sensitive(widget.get_active())

    def on_btnHelp_clicked(self, widget):
        # Open the help file as the real user (not root)
        shell_exec("xdg-open \"%s\"" % self.helpFile)

    # Close the gui
    def on_usbcreator_destroy(self, widget):
        # Close the app
        Gtk.main_quit()
    
    # ===============================================
    # Custom functions
    # ===============================================
    
    def refresh(self):
        self.udisks2.fill_devices()
        drives = self.udisks2.get_drives()
        force_changed = False
        if self.cmbDeviceHandler.getIndex() == 0:
            force_changed = True
        self.cmbDeviceHandler.fillComboBox(drives, 0)
        if force_changed:
            self.on_cmbDevice_changed()
            
    def get_iso_logo(self, search_string):
        search_string = search_string.lower()
        iso_logo = ''
        hkey = ''
        hratio = 0
        for key, logo in list(self.logos.items()):
            if key not in ["iso", "linux"]:
                ratio = get_fuzzy_ratio(key, search_string, 2)
                if ratio > 80:
                    if ratio > hratio or (ratio == hratio and len(key) > len(hkey)):
                        hratio = ratio
                        hkey = key
                        iso_logo = logo
        return iso_logo

    def fill_treeview_usbcreator(self, mount=''):
        isos_list = []
        # columns: checkbox, image (logo), device, driver
        column_types = ['bool', 'GdkPixbuf.Pixbuf', 'str', 'str']

        if exists(mount):
            isos = glob(join(mount, '*.iso'))
            for iso in isos:
                iso_name = basename(iso)
                iso_size = "{} MB".format(int(self.get_iso_size(iso) / 1024))
                # Try to get the logo by ISO name
                iso_logo = self.get_iso_logo(iso_name)
                if not iso_logo:
                    # Try to get the logo by ISO label
                    lbl = getoutput('usb-creator -l "{0}"'.format(iso))
                    if lbl:
                        iso_logo = self.get_iso_logo(lbl[0])
                if not iso_logo:
                    iso_logo = self.logos["iso"]
                self.log.write("ISO on {}: {}, {}, {}".format(mount, iso_name, iso_size, iso_logo))
                isos_list.append([False, iso_logo, iso_name, iso_size])

        # Fill treeview
        self.tvUsbIsosHandler.fillTreeview(contentList=isos_list, columnTypesList=column_types)

    def exec_command(self, command):
        try:
            # Run the command in a separate thread
            self.set_buttons_state(False)
            name = 'cmd'
            t = ExecuteThreadedCommands([command], self.queue)
            self.threads[name] = t
            t.daemon = True
            t.start()
            self.queue.join()
            GLib.timeout_add(1000, self.check_thread, name)

        except Exception as detail:
            ErrorDialog(self.btnExecute.get_label().replace('_', ''), detail)

    def check_thread(self, name):
        if self.threads[name].is_alive():
            self.set_progress()
            if not self.queue.empty():
                ret = self.queue.get()
                self.log.write("Queue returns: {}".format(ret), 'check_thread')
                self.queue.task_done()
                self.show_message(ret)
            return True

        # Thread is done
        self.log.write(">> Thread is done", 'check_thread')
        ret = 0
        if not self.queue.empty():
            ret = self.queue.get()
            self.queue.task_done()
        del self.threads[name]
        self.set_buttons_state(True)
        self.refresh()
        self.fill_treeview_usbcreator(self.device["mount"])
        self.set_statusbar_message("{}: {}".format(self.version_text, self.pck_version))
        self.show_message(ret)
        return False

    def set_buttons_state(self, enable):
        if not enable:
            # Disable buttons
            self.btnExecute.set_sensitive(False)
            self.btnDelete.set_sensitive(False)
            self.btnBrowseIso.set_sensitive(False)
            self.btnRefresh.set_sensitive(False)
            self.btnUnmount.set_sensitive(False)
            self.btnClear.set_sensitive(False)
            self.cmbDevice.set_sensitive(False)
            self.txtIso.set_sensitive(False)
            self.chkForceDistro.set_sensitive(False)
            self.chkPartition.set_sensitive(False)
            self.chkWriteSingle.set_sensitive(False)
        else:
            # Enable buttons and reset progress bar
            self.btnExecute.set_sensitive(True)
            self.btnDelete.set_sensitive(True)
            self.btnBrowseIso.set_sensitive(True)
            self.btnRefresh.set_sensitive(True)
            self.btnUnmount.set_sensitive(True)
            self.btnClear.set_sensitive(True)
            self.cmbDevice.set_sensitive(True)
            self.txtIso.set_sensitive(True)
            self.pbUsbCreator.set_fraction(0)
            self.cmbDistros.set_active(0)
            self.chkForceDistro.set_sensitive(True)
            self.chkPartition.set_sensitive(True)
            self.chkWriteSingle.set_sensitive(True)
            self.chkForceDistro.set_active(False)
            self.chkPartition.set_active(False)
            self.chkWriteSingle.set_active(False)

    def get_logos(self):
        logos_dict = {}
        logos_path = join(self.mediaDir, 'grub/themes/usb-creator/icons')
        logos = glob(join(logos_path, '*.png'))
        for logo in logos:
            key = splitext(basename(logo))[0]
            logos_dict[key] = logo
        return logos_dict

    def set_progress(self):
        if exists(self.log_file):
            msg = ''
            last_line = getoutput("tail -50 {} | grep -v DEBUG | grep -v ==".format(self.log_file))
            for line in reversed(last_line):
                # Check for session start line: that is the last line to check
                if ">>>>>" in line and "<<<<<" in line:
                    break
                for chk_line in self.log_lines:
                    if chk_line[0].lower() in line.lower():
                        # Message to show
                        msg = chk_line[2]
                        if chk_line[1] == 1:
                            # Set progress
                            match_obj = re.search(r'[0-9]+', line)
                            if match_obj:
                                if 'bytes' in line:
                                    iso_size = float(self.device["new_iso_required"])
                                    if iso_size > 0:
                                        # Calculate percentage from dd output
                                        perc = (float(match_obj.group(0)) / 1024) / iso_size
                                        #print((" dd: {}%").format(perc))
                                else:
                                    perc = float(match_obj.group(0)) / 100
                                self.pbUsbCreator.set_fraction(perc)
                        else:
                            # Just pulse
                            self.pbUsbCreator.pulse()
                        break
                if msg:
                    break
            self.set_statusbar_message(msg)

    def set_statusbar_message(self, message):
        if message is not None:
            context = self.statusbar.get_context_id('message')
            self.statusbar.push(context, message)

    def get_iso_size(self, iso):
        # Returns kilobytes
        total_size = 0
        if exists(iso):
            if isdir(iso):
                for dirpath, dirnames, filenames in os.walk(iso):
                    for f in filenames:
                        fp = join(dirpath, f)
                        # skip if it is symbolic link
                        if not islink(fp):
                            total_size += getsize(fp)
            else:
                total_size = getsize(iso)
        return (total_size / 1024)

    def show_message(self, cmdOutput):
        try:
            self.log.write("Command output: {}".format(cmdOutput), 'show_message')
            ret = int(cmdOutput)
            title = _("Error")
            if ret > 1 and ret != 255:
                if ret == 1:
                    ErrorDialog(title, _("Wrong arguments were passed."))
                elif ret == 2:
                    ErrorDialog(title, _("The device was not found."))
                elif ret == 3:
                    ErrorDialog(title, _("The device is not detachable."))
                elif ret == 4:
                    ErrorDialog(title, _("The device has no partition."))
                elif ret == 5:
                    ErrorDialog(title, _("Unable to mount the device."))
                elif ret == 6:
                    ErrorDialog(title, _("Given ISO path was not found."))
                elif ret == 7:
                    ErrorDialog(title, _("ISO too large for FAT formatted USB (max 4GB).\n"
                                         "Format the USB to exFAT, NTFS, ext4, etc."))
                elif ret == 8:
                    ErrorDialog(title, _("There is not enough space available on the device."))
                elif ret == 9:
                    ErrorDialog(title, _("Unable to determine the distribution name.\n"
                                         "Select a distribution in the 'Manual' section."))
                elif ret == 10:
                    ErrorDialog(title, _("Cannot find the target ISO file. Did you insert the USB?"))
                elif ret == 11:
                    ErrorDialog(title, _("Hash mismatch."))
                elif ret == 12:
                    ErrorDialog(title, _("Copy of ISO failed."))
                elif ret == 13:
                    ErrorDialog(title, _("Device is in use by another application."))
                else:
                    msg = _("An unknown error has occurred.")
                    ErrorDialog(title, msg)
            else:
                msg = _("The USB was successfully written.")
                MessageDialog(_("Finished"), msg)
        except:
            ErrorDialog(title, cmdOutput)

    # ===============================================
    # Language specific functions
    # ===============================================

    def get_language_dir(self):
        # First test if full locale directory exists, e.g. html/pt_BR,
        # otherwise perhaps at least the language is there, e.g. html/pt
        # and if that doesn't work, try html/pt_PT
        lang = self.get_current_language()
        path = join(self.htmlDir, lang)
        if not isdir(path):
            base_lang = lang.split('_')[0].lower()
            path = join(self.htmlDir, base_lang)
            if not isdir(path):
                path = join(self.htmlDir, "{}_{}".format(base_lang, base_lang.upper()))
                if not isdir(path):
                    path = join(self.htmlDir, 'en')
        return path

    def get_current_language(self):
        lang = os.environ.get('LANG', 'US').split('.')[0]
        if lang == '':
            lang = 'en'
        return lang
