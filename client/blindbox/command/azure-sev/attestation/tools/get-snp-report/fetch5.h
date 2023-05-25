/* Copyright (c) Microsoft Corporation.
   Licensed under the MIT License. */

#pragma once

bool fetchAttestationReport5(const char* report_data_hexstring, void **snp_report);

// does /dev/sev exists. This is where the PSP is exposed in 5.15.*
bool supportsDevSev();