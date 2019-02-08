# BMS-Software

Python 3 Software for the Battery Management System with Active Cell Balancing


## Python Script

The main python 3 script [`theBMS.py`](python/theBMS.py "theBMS.py") uses three classes as described below.

This main script is designed to run on a RPi Zero W and implements pushing to a MySQL databse as a proof of concept.

If this feature is not needed, comment out [line 95](python/theBMS.py#L95 "theBMS.py#L95") and [line 96](python/theBMS.py#L96 "theBMS.py#L96") in the file [`theBMS.py`](python/theBMS.py "theBMS.py"), otherwise modify the credentials / query.

### Classes

The classes [BMS](#bms "BMS"), [SunnyBoy](#sunnyboy "SunnyBoy") and [isoSPI](#isospi "isoSPI") are used.

#### BMS

The [BMS](python/classes/BMS.py "BMS.py") class models the whole battery management system (number of boards, voltages, ...).

#### SunnyBoy

The [SunnyBoy](python/classes/SunnyBoy.py "SunnyBoy.py") class models the fictional communication to a battery inverter called "Sunny Boy Storage 2.5".

#### isoSPI

The [isoSPI](python/classes/isoSPI.py "isoSPI.py") class handles the isolated SPI communication with the IC LTC6813-1. This is done by using a C++ program (see [Communication](#communication "Communication")). Furthermore the class is responsible for calculating and checking the package error code (PEC).

## Communication

Due to timing contrains, the actual isoSPI communication was implemented with a C++ program.

### Usage

```
This program must be run with superuser privileges.

Usage: ./isoSPI <cs> <spi> <boards> <cmd> [<data>...]

Options:
<cs>      Chip Select (CS) to use: (0 | 1)
<spi>     Number of SPI bytes to transfer: (0 | 1 | 2 | 3)
          0 meaning that this is not an SPI transaction
<boards>  Integer ranging from 1 to 50
<cmd>     4 bytes (32-bit) long command (unsigned decimal)
<data>    8 bytes (64-bit) long data (unsigned decimal)
```

To ensure that the program is always executed with superuser privileges (possible security threat!):

```bash
$ chmod 4775 isoSPI
$ sudo chown root isoSPI && sudo chgrp root isoSPI
```

### Examples

Commands are always sent to the IC LTC6813-1.

Sending commands to the IC LTC3300-1 (SPI > 0) is performed by an SPI transaction (from LTC6813-1 to LTC3300-1).

#### LTC6813-1

Send "Start Cell Voltage ADC Conversion and Poll Status (7kHz Mode, Discharge Not Permitted, All Cells)" command to all boards on isoSPI port 2 (CS 1):

```bash
$ ./isoSPI 1 0 2 56685676
```

Read "Cell Voltage Register Group A" from two boards on isoSPI port 1 (CS 0):

```bash
$ ./isoSPI 0 0 2 264130 0 0
```

Write "Configuration Register Group B" (GPIO6 Pin Pull-Down OFF: 1099511627776 or 0x10000000000) on three boards on isoSPI port 2 (CS 1):

```bash
$ ./isoSPI 1 0 3 2404766 72057594037993034 72057594037993034 72057594037993034
```

#### LTC3300-1

Send "Start Balancing Command" to one board on isoSPI port 1 (CS 0) by an SPI transaction (1 byte):

```bash
$ ./isoSPI 0 1 1 119612594 10014316694030852304
```

Send "Pause Balancing Command" to two boards on isoSPI port 2 (CS 1) by an SPI transaction (1 byte):

```bash
$ ./isoSPI 1 1 2 119612594 10009813094403507264 10009813094403507264
```

Send "Write and Execute Balancing Command" to two boards on isoSPI port 1 (CS 0) by an SPI transaction (3 bytes). In this example, cell 6 is discharged and cell 1 is charged (Balancing Command: 0xC02 or 0b1100 0000 0010):

```bash
$ ./isoSPI 0 3 2 119612594 9986886141864380864 9986886141864380864
```

## Download

* [**isoSPI v1.0.1**](https://github.com/MuellerDominik/BMS-Software/releases/download/v1.0.1/isoSPI "isoSPI v1.0.1") - Latest binary release (NOT YET UPLOADED)

```bash
$ sha256sum isoSPI
[NOT YET COMPUTED]  isoSPI
```

The C++ file [`isoSPI.cc`](cc/isoSPI.cc "isoSPI.cc") was compiled on the Raspberry Pi Zero W with the following command:

```bash
$ g++ isoSPI.cc -o isoSPI -lbcm2835
```

## Changelog

* **v1.0.1**
  * Adjusted the value of the series resistance (temperature measurement) to the nominal value.
  * Adjusted the nominal value of the series resistance (comment).
* **v1.0.0**
  * Initial release

## License

Copyright &copy; 2018 pro3E - Team4

This project is licensed under the MIT License - see the [LICENSE](LICENSE "LICENSE") file for details
