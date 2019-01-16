#include <bcm2835.h>
#include <iostream>
#include <iomanip>

int main(int argc, char** argv) {
	char *end = NULL;

	unsigned cs = atoi(argv[1]);
	unsigned spi = atoi(argv[2]);
	unsigned boards = atoi(argv[3]);
	unsigned long cmd = strtoul(argv[4], &end, 10);

	unsigned bytes = 4 + (argc - 5)*8; // 4 CMD bytes + DATA bytes
	unsigned spi_bytes = spi * 3;

	char buff[bytes];
	char spi_exec[4 + spi_bytes] = {0x7, 0x23, 0xb9, 0xe4}; // SPI execute CMD
	char spi_read[4 + boards*8] = {0x7, 0x22, 0x32, 0xd6}; // Readback SPI answer

	for(int i = 3; i >= 0; --i) {
		unsigned long byte_mask = 0xff;
		buff[3 - i] = (char) ((cmd & (byte_mask << i*8)) >> i*8); // Add CMD bytes
	}

	if(argc > 5) {
		for(unsigned i = 0; i < (argc - 5); ++i) {
			unsigned long long byte_mask = 0xff;
			unsigned long long tmp = strtoull(argv[i + 5], &end, 10);
			for(int j = 7; j >= 0; --j) {
				buff[i*8 + 11 - j] = (tmp & (byte_mask << j*8)) >> j*8; // Add DATA bytes
			}
		}
	}

	if(spi) {
		for(unsigned i = 0; i < spi_bytes; ++i) {
			spi_exec[4 + i] = 0x0;
		}
		for(unsigned i = 0; i < boards*8; ++i) {
			spi_read[4 + i] = 0x0;
		}
	}

	if (!bcm2835_init()) {
		std::cout << "INIT failed!" << std::endl;
		return 1;
	}

	if(!bcm2835_spi_begin()) {
		std::cout << "SPI begin failed!" << std::endl;
		return 1;
	}

	// Configure BCM2835
	bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST); // MSB First
	bcm2835_spi_setDataMode(BCM2835_SPI_MODE0); // Polarity = 0 | Phase = 0
	bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_512); // 488 kHz
	bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW); // Active Low CS0
	bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, LOW); // Active Low CS1

	// Select CS0 or CS1
	if(cs) {
		bcm2835_spi_chipSelect(BCM2835_SPI_CS1);
	} else {
		bcm2835_spi_chipSelect(BCM2835_SPI_CS0);
	}

	// Wakeup all the boards
	for(unsigned i = 0; i < boards; ++i) {
		bcm2835_spi_transfer(0x0);
		bcm2835_delay(1);
	}

	bcm2835_spi_transfern(buff, bytes);

	if(spi) {
		bcm2835_spi_transfern(spi_exec, 4 + spi_bytes);
		bcm2835_spi_transfern(spi_read, 4 + boards*8);
	}

	bcm2835_spi_end();
	bcm2835_close();

	if(spi) {
		for(int i = 0; i < boards*8; ++i) {
			std::cout << std::internal << std::setfill('0') << std::setw(2) << std::hex << (int) spi_read[i + 4];
		}
	} else {
		for(int i = 0; i < bytes - 4; ++i) {
			std::cout << std::internal << std::setfill('0') << std::setw(2) << std::hex << (int) buff[i + 4];
		}
	}

	return 0;
}
