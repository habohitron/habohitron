#include <stdlib.h>
#include <stdio.h>
#include <time.h> 
#include <openssl/des.h>

#define GOTO_RET(err, marker) \
	ret = err; \
	goto marker;
	
int main(int argc, char **argv)
{
	int ret = EXIT_SUCCESS;
	FILE *in = NULL, *out = NULL;
	DES_cblock block, key;
	DES_key_schedule schedule;
	
	// TODO: replace with real key
	srand (time(NULL));
	DES_random_key(&key);
	printf("%02x %02x %02x %02x %02x %02x %02x %02x\n", key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7]);
	
	in = fopen("./cmconfig.cfg", "rb");
	if(in == NULL) {
		printf("could not open cmconfig.cfg\n");
		GOTO_RET(EXIT_FAILURE, end);
	}
	out = fopen("./cmconfig_dec.cfg", "wb");
	if(out == NULL) {
		printf("could not open cmconfig_dec.cfg\n");
		GOTO_RET(EXIT_FAILURE, close_in);
	}
	
	DES_set_key_unchecked(&key, &schedule);
	while(fread((void *)&block, sizeof(block), 1, in) > 0) {
		DES_ecb_encrypt(&block, &block, &schedule, 1);
		fwrite((void *)&block, sizeof(block), 1, out);
	}
close_out:
	fclose(out);
close_in:
	fclose(in);
end:
	return ret;
}
