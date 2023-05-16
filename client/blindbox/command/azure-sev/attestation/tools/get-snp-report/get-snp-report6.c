#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <memory.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>

#include "snp-attestation.h"
#include "snp-ioctl6.h"
#include "helpers.h"

bool supportsDevSevGuest()
{
    return access("/dev/sev-guest", W_OK) == 0;
}

bool fetchAttestationReport6(const char* report_data_hexstring, void **snp_report)
{
    int fd;
    int rc;

    fd = open("/dev/sev-guest", O_RDWR | O_CLOEXEC);

    if (fd < 0) {
        fprintf(stdout, "Failed to open /dev/sev-guest\n");        
        return false;
    }

    // this is the request, mostly the report data, vmpl
    snp_report_req snp_request;
    // and the result from the ioctl, in the get report case this will be the report
    snp_report_resp snp_response;
    
    // the object we pass to the ioctl that wraps the psp request.
    snp_guest_request_ioctl ioctl_request;

    memset(&snp_request, 0, sizeof(snp_request));
    
    // the report data is passed as a hexstring which needs to be decoded into an array of 
    // unsigned bytes
    // MAA expects a SHA-256. So we use left align the bytes in the report data.

    uint8_t *reportData = decodeHexString(report_data_hexstring, sizeof(snp_request.report_data));   
    memcpy(snp_request.report_data, reportData, sizeof(snp_request.report_data));

    memset(&snp_response, 0, sizeof(snp_response));
    memset(&ioctl_request, 0, sizeof(ioctl_request));
    
    ioctl_request.msg_version = 1;
    ioctl_request.req_data = (uint64_t)&snp_request;
    ioctl_request.resp_data = (uint64_t)&snp_response;

    rc = ioctl(fd, SNP_GET_REPORT, &ioctl_request);

    if (rc < 0) {
        fprintf(stderr, "Failed to issue ioctl SEV_SNP_GUEST_MSG_REPORT\n");        
        return false;  
    }
    
    msg_response_resp *response = (msg_response_resp *)&snp_response.data;
    snp_attestation_report *report = &response->report;


    *snp_report = (snp_attestation_report *) malloc (sizeof(snp_attestation_report));        
    memcpy(*snp_report, report, sizeof(snp_attestation_report));

    return true;
}
