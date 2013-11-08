/*
	$ gcc -o hc -s -O3 hc.c -lcrypto
	$ hc cmconfig.cfg cmconfig_plain.txt d # decrypting
	$ hc cmconfig_plain.txt cmconfig.cfg e # encrypting
*/
#include <stdlib.h>
#include <stdio.h>
#include <openssl/des.h>
	
#define RET_GOTO(code, marker) \
	ret = code; \
	goto marker;
	
// libhtx_db.so:00059B14
static DES_cblock hitron_key = {
	0x57, 0x8A, 0x95, 0x8E, 0x3D, 0xD9, 0x33, 0xFC
};

void hitron_crypt(FILE *out, FILE *in, int enc)
{
	DES_cblock block;
	DES_key_schedule schedule;
	DES_set_key_unchecked(&hitron_key, &schedule);
	while(fread((void *)&block, sizeof(block), 1, in) > 0) {
		DES_ecb_encrypt(&block, &block, &schedule, enc);
		fwrite((void *)&block, sizeof(block), 1, out);
	}
}

int main(int argc, char **argv)
{
	int ret = EXIT_SUCCESS;
	FILE *in = NULL, *out = NULL;

	if(argc != 4) {
		printf("Usage: hc in out d|e");
		return EXIT_FAILURE;
	}
		
	in = fopen(argv[1], "rb");
	if(in == NULL) {
		printf("could not open file\n");
		return EXIT_FAILURE;
	}
	
	out = fopen(argv[2], "wb");
	if(out == NULL) {
		printf("could not open file\n");
		RET_GOTO(EXIT_FAILURE, close_in);
	}
	hitron_crypt(out, in, argv[3][0] == 'e');
	
	fclose(out);
close_in:
	fclose(in);
end:
	return EXIT_SUCCESS;
}
