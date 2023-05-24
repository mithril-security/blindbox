/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>

#include "snp-attestation.h"
#include "snp-ioctl5.h"

#include "helpers.h"

bool supportsDevSev()
{
    return access("/dev/sev", W_OK) == 0;
}

bool fetchAttestationReport5(const char* report_data_hexstring, void **snp_report)
{
    msg_report_req msg_report_in;    
    msg_response_resp msg_report_out;
    
    int fd, rc;
    
    struct sev_snp_guest_request payload = {
        .req_msg_type = SNP_MSG_REPORT_REQ,
        .rsp_msg_type = SNP_MSG_REPORT_RSP,
        .msg_version = 1,        
        .request_len = sizeof(msg_report_in),
        .request_uaddr = (uint64_t) (void*) &msg_report_in,
        .response_len = sizeof(msg_report_out),
        .response_uaddr = (uint64_t) (void*) &msg_report_out,
        .error = 0
    };
    
    memset((void*) &msg_report_in, 0, sizeof(msg_report_in));        
    memset((void*) &msg_report_out, 0, sizeof(msg_report_out));

    // the report data is passed as a hexstring which needs to be decoded into an array of 
    // unsigned bytes
    // MAA expects a SHA-256. So we use left align the bytes in the report data
    
    uint8_t *reportData = decodeHexString(report_data_hexstring, sizeof(msg_report_in.report_data));   
    memcpy(msg_report_in.report_data, reportData, sizeof(msg_report_in.report_data));

    // open the file descriptor of the PSP
    fd = open("/dev/sev", O_RDWR | O_CLOEXEC);

    if (fd < 0) {
        fprintf(stderr, "Failed to open /dev/sev\n");        
        return false;
    }

    // issue the custom SEV_SNP_GUEST_MSG_REPORT sys call to the sev driver
    rc = ioctl(fd, SEV_SNP_GUEST_MSG_REPORT, &payload);

    if (rc < 0) {
        fprintf(stderr, "Failed to issue ioctl SEV_SNP_GUEST_MSG_REPORT\n");        
        return false;    
    }

    #ifdef DEBUG_OUTPUT   
    fprintf(stderr, "Response header:\n");
    uint8_t *hdr = (uint8_t*) &msg_report_out;
    
    for (size_t i = 0; i < 32; i++) {
        fprintf(stderr, "%02x", hdr[i]);
        if (i % 16 == 15)
            fprintf(stderr, "\n");
        else
            fprintf(stderr, " ");
    }
    fprintf(stderr, "Attestation report:\n");
    printReport(&msg_report_out.report);
    #endif

    *snp_report = (snp_attestation_report *) malloc (sizeof(snp_attestation_report));        
    memcpy(*snp_report, &msg_report_out.report, sizeof(snp_attestation_report));

    return true;
}
