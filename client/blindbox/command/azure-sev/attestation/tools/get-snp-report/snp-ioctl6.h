/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#pragma once


#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdint.h>

/* linux kernel 6.* versions of the ioctls that talk to the PSP */

/* From sev-snp driver include/uapi/linux/psp-sev-guest.h */

struct sev_snp_guest_request {
    uint8_t req_msg_type;
    uint8_t rsp_msg_type;
    uint8_t msg_version;
    uint16_t request_len;
    uint64_t request_uaddr;
    uint16_t response_len;
    uint64_t response_uaddr;
    uint32_t error;            /* firmware error code on failure (see psp-sev.h) */
};

// aka/replaced by this from include/uapi/linux/sev-guest.h
//
typedef struct {
    /* message version number (must be non-zero) */
    uint8_t msg_version;

    /* Request and response structure address */
    uint64_t req_data;
    uint64_t resp_data;

    /* firmware error code on failure (see psp-sev.h) */
    uint64_t fw_err;
} snp_guest_request_ioctl;

enum snp_msg_type {
    SNP_MSG_TYPE_INVALID = 0,
    SNP_MSG_CPUID_REQ,
    SNP_MSG_CPUID_RSP,
    SNP_MSG_KEY_REQ,
    SNP_MSG_KEY_RSP,
    SNP_MSG_REPORT_REQ,
    SNP_MSG_REPORT_RSP,
    SNP_MSG_EXPORT_REQ,
    SNP_MSG_EXPORT_RSP,
    SNP_MSG_IMPORT_REQ,
    SNP_MSG_IMPORT_RSP,
    SNP_MSG_ABSORB_REQ,
    SNP_MSG_ABSORB_RSP,
    SNP_MSG_VMRK_REQ,
    SNP_MSG_VMRK_RSP,
    SNP_MSG_TYPE_MAX
};

#define SNP_GUEST_REQ_IOC_TYPE        'S'
#define SNP_GET_REPORT                _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, snp_guest_request_ioctl)
#define SNP_GET_DERIVED_KEY           _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x1, snp_guest_request_ioctl)
#define SNP_GET_EXT_REPORT            _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x2, snp_guest_request_ioctl)

/* from SEV-SNP Firmware ABI Specification Table 20 */

typedef struct {
    uint8_t report_data[64];
    uint32_t vmpl;
    uint8_t reserved[28]; // needs to be zero
} snp_report_req; // aka snp_report_req in (linux) include/uapi/linux/sev-guest.h

typedef struct {
/* response data, see SEV-SNP spec for the format */
    uint8_t  data[4000];
} snp_report_resp;
