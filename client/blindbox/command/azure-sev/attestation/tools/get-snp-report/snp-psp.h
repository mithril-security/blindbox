/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#pragma once

#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdint.h>

/* From sev-snp driver include/uapi/linux/psp-sev-guest.h */
struct sev_snp_guest_request {
    uint8_t req_msg_type;
    uint8_t rsp_msg_type;
    uint8_t msg_version;
    uint16_t request_len;
    uint64_t request_uaddr;
    uint16_t response_len;
    uint64_t response_uaddr;
    uint32_t error;           /* firmware error code on failure (see psp-sev.h) */
};

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


#define SEV_GUEST_IOC_TYPE           'S'
#define SEV_SNP_GUEST_MSG_REQUEST    _IOWR(SEV_GUEST_IOC_TYPE, 0x0, struct sev_snp_guest_request)
#define SEV_SNP_GUEST_MSG_REPORT     _IOWR(SEV_GUEST_IOC_TYPE, 0x1, struct sev_snp_guest_request)
#define SEV_SNP_GUEST_MSG_KEY        _IOWR(SEV_GUEST_IOC_TYPE, 0x2, struct sev_snp_guest_request)
