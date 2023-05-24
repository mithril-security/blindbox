/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#pragma once

bool fetchAttestationReport6(const char* report_data_hexstring, void **snp_report);

// 6.1 linux exposees the PSP via /dev/sev-guest

bool supportsDevSevGuest();
