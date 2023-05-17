// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package attest

import (
	"encoding/base64"
	"encoding/hex"
	"fmt"

	"io/ioutil"
	"os"

	"ACI_Attest/common"
	"github.com/pkg/errors"
	_ "github.com/sirupsen/logrus"
)

// CertState contains information about the certificate cache service
// that provides access to the certificate chain required upon attestation
type CertState struct {
	CertFetcher CertFetcher `json:"cert_cache"`
	Tcbm        uint64      `json:"tcbm"`
}

func GetSNPReport(securityPolicy string, runtimeDataBytes []byte) ([]byte, []byte, error) {
	// check if sev device exists on the platform; if not return an error
	fetchRealSNPReport := true
	if _, err := os.Stat("/dev/sev"); errors.Is(err, os.ErrNotExist) {
		// dev/sev doesn't exist, check dev/sev-guest
		if _, err := os.Stat("/dev/sev-guest"); errors.Is(err, os.ErrNotExist) {
			// dev/sev-guest doesn't exist
			return nil, nil, errors.Wrapf(err, "fetching snp report failed")
		}
	}

	inittimeDataBytes, err := base64.StdEncoding.DecodeString(securityPolicy)
	if err != nil {
		return nil, nil, errors.Wrap(err, "decoding policy from Base64 format failed")
	}

	SNPReportBytes, err := FetchSNPReport(fetchRealSNPReport, runtimeDataBytes, inittimeDataBytes)
	if err != nil {
		return nil, nil, errors.Wrapf(err, "fetching snp report failed")
	}

	if common.GenerateTestData {
		ioutil.WriteFile("snp_report.bin", SNPReportBytes, 0644)
	}

	return SNPReportBytes, inittimeDataBytes, nil
}

func (certState *CertState) RefreshCertChain(SNPReport SNPAttestationReport) ([]byte, error) {
	// TCB values not the same, try refreshing cert first
	vcekCertChain, thimTcbm, err := certState.CertFetcher.GetCertChain(SNPReport.ChipID, SNPReport.ReportedTCB)
	if err != nil {
		return nil, errors.Wrap(err, "refreshing CertChain failed")
	}
	certState.Tcbm = thimTcbm
	return vcekCertChain, nil
}

// RawAttest returns the raw attestation report in hex string format
func RawAttest(inittimeDataBytes []byte, runtimeDataBytes []byte) (string, error) {
	// check if sev device exists on the platform; if not return an error
	fetchRealSNPReport := true
	if _, err := os.Stat("/dev/sev"); errors.Is(err, os.ErrNotExist) {
		// dev/sev doesn't exist, check dev/sev-guest
		if _, err := os.Stat("/dev/sev-guest"); errors.Is(err, os.ErrNotExist) {
			// dev/sev-guest doesn't exist
			return "", errors.Wrapf(err, "fetching snp report failed")
		}
	}

	SNPReportBytes, err := FetchSNPReport(fetchRealSNPReport, runtimeDataBytes, inittimeDataBytes)
	if err != nil {
		return "", errors.Wrapf(err, "fetching snp report failed")
	}

	return hex.EncodeToString(SNPReportBytes), nil
}

// Attest interacts with maa services to fetch an MAA token
// MAA expects four attributes:
// (A) the attestation report signed by the PSP signing key
// (B) a certificate chain that endorses the signing key of the attestation report
// (C) reference information that provides evidence that the UVM image is genuine.
// (D) inittime data: this is the policy blob that has been hashed by the host OS during the utility
//
//	VM bringup and has been reported by the PSP in the attestation report as HOST DATA
//
// (E) runtime data: for example it may be a wrapping key blob that has been hashed during the attestation report
//
//	retrieval and has been reported by the PSP in the attestation report as REPORT DATA
func (certState *CertState) Attest(maa MAA, runtimeDataBytes []byte, uvmInformation common.UvmInformation) (string, error) {
	// Fetch the attestation report
	SNPReportBytes, inittimeDataBytes, err := GetSNPReport(uvmInformation.EncodedSecurityPolicy, runtimeDataBytes)
	if err != nil {
		return "", errors.Wrapf(err, "failed to retrieve attestation report")
	}

	// Retrieve the certificate chain using the chip identifier and platform version
	// fields of the attestation report
	var SNPReport SNPAttestationReport
	if err = SNPReport.DeserializeReport(SNPReportBytes); err != nil {
		return "", errors.Wrapf(err, "failed to deserialize attestation report")
	}

	// At this point check that the TCB of the cert chain matches that reported so we fail early or
	// fetch fresh certs by other means.
	var vcekCertChain []byte
	if SNPReport.ReportedTCB != certState.Tcbm {
		// TCB values not the same, try refreshing cert cache first
		vcekCertChain, err = certState.RefreshCertChain(SNPReport)
		if err != nil {
			return "", err
		}

		if SNPReport.ReportedTCB != certState.Tcbm {
			// TCB values still don't match, try retrieving the SNP report again
			SNPReportBytes, inittimeDataBytes, err = GetSNPReport(uvmInformation.EncodedSecurityPolicy, runtimeDataBytes)
			if err != nil {
				return "", errors.Wrapf(err, "failed to retrieve new attestation report")
			}

			if err = SNPReport.DeserializeReport(SNPReportBytes); err != nil {
				return "", errors.Wrapf(err, "failed to deserialize new attestation report")
			}

			// refresh certs again
			vcekCertChain, err = certState.RefreshCertChain(SNPReport)
			if err != nil {
				return "", err
			}

			// if no match after refreshing certs and attestation report, fail
			if SNPReport.ReportedTCB != certState.Tcbm {
				return "", errors.New(fmt.Sprintf("SNP reported TCB value: %d doesn't match Certificate TCB value: %d", SNPReport.ReportedTCB, certState.Tcbm))
			}
		}
	} else {
		certString := uvmInformation.InitialCerts.VcekCert + uvmInformation.InitialCerts.CertificateChain
		vcekCertChain = []byte(certString)
	}

	uvmReferenceInfoBytes, err := base64.StdEncoding.DecodeString(uvmInformation.EncodedUvmReferenceInfo)

	if err != nil {
		return "", errors.Wrap(err, "decoding policy from Base64 format failed")
	}

	// Retrieve the MAA token required by the request's MAA endpoint
	maaToken, err := maa.attest(SNPReportBytes, vcekCertChain, inittimeDataBytes, runtimeDataBytes, uvmReferenceInfoBytes)
	if err != nil || maaToken == "" {
		return "", errors.Wrapf(err, "retrieving MAA token from MAA endpoint failed")
	}

	return maaToken, nil
}
