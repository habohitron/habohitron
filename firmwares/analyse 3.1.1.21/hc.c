/*
	$ gcc -o hc -s -O3 hc.c -lcrypto
*/
#include <stdlib.h>
#include <stdio.h>
#include <openssl/des.h>
	
// libhtx_db.so:00059B14
static DES_cblock hitron_key = {
	0x57, 0x8A, 0x95, 0x8E, 0x3D, 0xD9, 0x33, 0xFC
};

void hitron_crypt(FILE *out, FILE *in)
{
	DES_cblock block;
	DES_key_schedule schedule;
	DES_set_key_unchecked(&hitron_key, &schedule);
	while(fread((void *)&block, sizeof(block), 1, in) > 0) {
		DES_ecb_encrypt(&block, &block, &schedule, 0);
		fwrite((void *)&block, sizeof(block), 1, out);
	}
}

int main(int argc, char **argv)
{
	FILE *in = NULL;

	if(argc != 2) {
		printf("Usage: hc cmconfig.cfg");
		return EXIT_FAILURE;
	}
	
	in = fopen(argv[1], "rb");
	if(in == NULL) {
		printf("could not open file\n");
		return EXIT_FAILURE;
	}
	hitron_crypt(stdout, in);
	fclose(in);

	return EXIT_SUCCESS;
}
