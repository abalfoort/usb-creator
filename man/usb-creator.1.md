---
layout: page
title: USB-CREATOR
section: 1
footer: "USB Creator"
header: "USB Creator"
date: September 2020
---

# NAME

usb-creator - Multiboot USB Creator

# SYNOPSIS

**usb-creator** \[OPTIONS\] \[PATH_TO_ISO\] \[DEVICE\]

# DESCRIPTION

USB Creator create a bootable USB with multiple ISO images.

The application has a GUI but can also be used from the terminal.

For terminal use, see options below.

-D
:   Show all supported distribution names.

-d \[family_name\]
:   Show supported distribution names by family name

-f \[distribution_name\]
:   Force distribution name (see -D or -d parameter)

-h
:   Help screen.

-l \[path_to_iso\]
:   Show ISO label

-p
:   Partition the USB device

-r
:   Remove the ISO from the USB device.

-s \[path_to_iso\]
:   Show distribution name from ISO path

-u
:   Unpack ISO to USB device

-v
:   Starts GUI with verbose output

No parameters
:   Start the GUI


# FILES

*~/.usb-creator/usb-creator.log

:   Per-user log file.

# Author

Written by Arjen Balfoort

# BUGS

https://gitlab.com/abalfoort/usb-creator/-/issues


