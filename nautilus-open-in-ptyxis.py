#!/usr/bin/python3
import shutil
import subprocess
import urllib.parse

from gi import require_version

require_version("Nautilus", "4.0")
require_version("Gtk", "4.0")

TERMINAL_NAME = "app.devsuite.Ptyxis"

import logging
import os
from gettext import gettext

from gi.repository import GObject, Nautilus

if os.environ.get("NAUTILUS_PTYXIS_DEBUG", "False") == "True":
    logging.basicConfig(level=logging.DEBUG)


class PtyxisNautilus(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.is_select = False
        pass

    def get_file_items(self, files: list[Nautilus.FileInfo]):
        """Return to menu when click on any file/folder"""
        if not self.only_one_file_info(files):
            return []

        menu = []
        fileInfo = files[0]
        self.is_select = False

        if fileInfo.is_directory():
            self.is_select = True
            dir_path = self.get_abs_path(fileInfo)

            logging.debug("Selecting a directory!!")
            logging.debug(f"Create a menu item for entry {dir_path}")
            menu_item = self._create_nautilus_item(dir_path)
            menu.append(menu_item)

        return menu

    def get_background_items(self, directory):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""
        # Some concurrency problem fix.
        # when you select a directory, and right mouse, nautilus will call this
        # once the moments you focus the menu. This code to ignore that time.
        if self.is_select:
            self.is_select = False
            return []

        menu = []
        if directory.is_directory():
            dir_path = self.get_abs_path(directory)

            logging.debug("Not thing is selected. Launch from backgrounds!!")
            logging.debug(f"Create a menu item for entry {dir_path}")
            menu_item = self._create_nautilus_item(dir_path)
            menu.append(menu_item)

        return menu

    def _create_nautilus_item(self, dir_path: str) -> Nautilus.MenuItem:
        """Creates the 'Open In Ptyxis' menu item."""

        item = Nautilus.MenuItem(
            name="PtyxisNautilus::open_in_ptyxis",
            label=gettext("Open in Ptyxis"),
            tip=gettext("Open this folder/file in Ptyxis Terminal"),
        )
        logging.debug(f"Created item with path {dir_path}")

        item.connect("activate", self._nautilus_run, dir_path)
        logging.debug("Connect trigger to menu item")

        return item

    def is_native(self):
        if shutil.which("ptyxis-terminal") == "/usr/bin/ptyxis-terminal":
            return "ptyxis-terminal"
        if shutil.which("ptyxis") == "/usr/bin/ptyxis":
            return "ptyxis"

    def _nautilus_run(self, menu, path):
        """'Open with Ptyxis's menu item callback."""
        logging.debug("Openning:", path)
        args = None
        if self.is_native()=="ptyxis-terminal":
            args = ["ptyxis-terminal", "--new-window", "-d", path]
        elif self.is_native()=="ptyxis":
            args = ["ptyxis", "--new-window", "-d", path]
        else:
            args = ["/usr/bin/flatpak", "run", TERMINAL_NAME, "--new-window", "-d", path]

        subprocess.Popen(args, cwd=path)

    def get_abs_path(self, fileInfo: Nautilus.FileInfo):
        path = fileInfo.get_location().get_path()
        return path

    def only_one_file_info(self, files: list[Nautilus.FileInfo]):
        return len(files) == 1
