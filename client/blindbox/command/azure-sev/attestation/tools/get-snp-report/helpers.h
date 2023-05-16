/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#pragma once

#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>

#include "snp-attestation.h"


#define PRINT_VAL(ptr, field) printBytes(#field, (const uint8_t *)&(ptr->field), sizeof(ptr->field), true)
#define PRINT_BYTES(ptr, field) printBytes(#field, (const uint8_t *)&(ptr->field), sizeof(ptr->field), false)

// Helper functions
uint8_t* decodeHexString(const char *hexstring, size_t padTo);

char* encodeHexToString(uint8_t byte_array[], size_t len);

void printBytes(const char *desc, const uint8_t *data, size_t len, bool swap);

void printReport(const snp_attestation_report *r);