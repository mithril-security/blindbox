#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>

#include "snp-ioctl5.h"

#include "helpers.h"



// Helper functions
uint8_t* decodeHexString(const char *hexstring, size_t padTo) // will zero pad to bufferLen
{   
    size_t len = strlen(hexstring);
    size_t out_len = len/2+1;
    if (out_len < padTo)
        out_len = padTo;
    uint8_t *byte_array = (uint8_t*) malloc(out_len);
    memset(byte_array, 0, out_len);
    
    for (size_t i = 0; i < len; i+=2) {        
        sscanf(hexstring, "%2hhx", &byte_array[i/2]);
        hexstring += 2;        
    }

    return byte_array;
}

char* encodeHexToString(uint8_t byte_array[], size_t len)
{    
    char* hexstring = (char*) malloc((2*len+1)*sizeof(char));

    for (size_t i = 0; i < len; i++)       
        sprintf(&hexstring[i*2], "%02x", byte_array[i]);                    
    
    hexstring[2*len] = '\0'; // string padding character    
    return hexstring;
}

void printBytes(const char *desc, const uint8_t *data, size_t len, bool swap)
{
    fprintf(stderr, "  %s: ", desc);
    int padding = 20 - strlen(desc);
    if (padding < 0)
        padding = 0;
    for (int count = 0; count < padding; count++)
        putchar(' ');

    for (size_t pos = 0; pos < len; pos++) {
        fprintf(stderr, "%02x", data[swap ? len - pos - 1 : pos]);
        if (pos % 32 == 31)
            printf("\n                        ");
        else if (pos % 16 == 15)
            putchar(' ');
    }
    fprintf(stderr, "\n");
}

void printReport(const snp_attestation_report *r)
{    
    PRINT_VAL(r, version);
    PRINT_VAL(r, guest_svn);
    PRINT_VAL(r, policy);
    PRINT_VAL(r, family_id);
    PRINT_VAL(r, image_id);
    PRINT_VAL(r, vmpl);
    PRINT_VAL(r, signature_algo);
    PRINT_BYTES(r, platform_version);
    PRINT_BYTES(r, platform_info);
    PRINT_VAL(r, author_key_en);
    PRINT_VAL(r, reserved1);
    PRINT_BYTES(r, report_data);
    PRINT_BYTES(r, measurement);
    PRINT_BYTES(r, host_data);
    PRINT_BYTES(r, id_key_digest);
    PRINT_BYTES(r, author_key_digest);
    PRINT_BYTES(r, report_id);
    PRINT_BYTES(r, report_id_ma);
    PRINT_VAL(r, reported_tcb);
    PRINT_BYTES(r, reserved2);
    PRINT_BYTES(r, chip_id);
    PRINT_BYTES(r, reserved3);
    PRINT_BYTES(r, signature);
}