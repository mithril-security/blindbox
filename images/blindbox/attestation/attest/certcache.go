// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package attest

/*
	This is not currently strictly required as these platform certificates from AMD are
	now provided by GCS to containers as an environment variable UVM_HOST_AMD_CERTIFICATE

	It is required for the tests and when running outside of Azure.
*/

import (
	"encoding/binary"
	"encoding/pem"
	"fmt"
	"strconv"

	"crypto/x509"

	"ACI_Attest/common"
	"github.com/pkg/errors"
)

const (
	AzureCertCacheRequestURITemplate = "https://%s/%s/certificates/%s/%s?%s"
	AmdVCEKRequestURITemplate        = "https://%s/%s/%s?ucodeSPL=%d&snpSPL=%d&teeSPL=%d&blSPL=%d"
	AmdCertChainRequestURITemplate   = "https://%s/%s/cert_chain"
	LocalTHIMUriTemplate             = "https://%s" // To-Do update once we know what this looks like
)

const (
	BlSplTcbmByteIndex    = 0
	TeeSplTcbmByteIndex   = 1
	TcbSpl_4TcbmByteIndex = 2
	TcbSpl_5TcbmByteIndex = 3
	TcbSpl_6TcbmByteIndex = 4
	TcbSpl_7TcbmByteIndex = 5
	SnpSplTcbmByteIndex   = 6
	UcodeSplTcbmByteIndex = 7
)

// can't find any documentation on why the 3rd byte of the Certificate.Extensions byte array is the one that matters
// all the byte arrays for the tcb values are of length 3 and fit the format [2 1 IMPORTANT_VALUE]
const x509CertExtensionsValuePos = 2

// parses the cached CertChain and returns the VCEK leaf certificate
// Subject of the (x509) VCEK certificate (CN=SEV-VCEK)
func GetVCEKFromCertChain(certChain []byte) (*x509.Certificate, error) {
	currChain := certChain
	// iterate through the certificates in the chain
	for len(currChain) > 0 {
		var block *pem.Block
		block, currChain = pem.Decode(currChain)
		if block.Type == "CERTIFICATE" {
			certificate, err := x509.ParseCertificate(block.Bytes)
			if err != nil {
				return nil, err
			}
			// check if this is the correct certificate
			if certificate.Subject.CommonName == "SEV-VCEK" {
				return certificate, nil
			}
		}
	}
	return nil, errors.New("No certificate chain found")
}

// parses the VCEK certificate to return the TCB version
// fields reprocessed back into a uint64 to compare against the `ReportedTCB` in the fetched attestation report
func ParseVCEK(certChain []byte) ( /*tcbVersion*/ uint64, error) {
	vcekCert, err := GetVCEKFromCertChain(certChain)
	if err != nil {
		return 0, err
	}

	tcbValues := make([]byte, 8) // TCB version is 8 bytes
	// parse extensions to update the THIM URL and get TCB Version
	for _, ext := range vcekCert.Extensions {
		switch ext.Id.String() {

		// blSPL
		case "1.3.6.1.4.1.3704.1.3.1":
			tcbValues[BlSplTcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// teeSPL
		case "1.3.6.1.4.1.3704.1.3.2":
			tcbValues[TeeSplTcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// spl_4
		case "1.3.6.1.4.1.3704.1.3.4":
			tcbValues[TcbSpl_4TcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// spl_5
		case "1.3.6.1.4.1.3704.1.3.5":
			tcbValues[TcbSpl_5TcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// spl_6
		case "1.3.6.1.4.1.3704.1.3.6":
			tcbValues[TcbSpl_6TcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// spl_7
		case "1.3.6.1.4.1.3704.1.3.7":
			tcbValues[TcbSpl_7TcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// snpSPL
		case "1.3.6.1.4.1.3704.1.3.3":
			tcbValues[SnpSplTcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		// ucodeSPL
		case "1.3.6.1.4.1.3704.1.3.8":
			tcbValues[UcodeSplTcbmByteIndex] = ext.Value[x509CertExtensionsValuePos]
		}
	}

	return binary.LittleEndian.Uint64(tcbValues), nil
}

// CertFetcher contains information about the certificate cache service
// that provides access to the certificate chain required upon attestation
type CertFetcher struct {
	EndpointType string `json:"endpoint_type"` // AMD, AzCache, LocalTHIM
	Endpoint     string `json:"endpoint"`
	TEEType      string `json:"tee_type,omitempty"`
	APIVersion   string `json:"api_version,omitempty"`
}

// retrieveCertChain interacts with the cert cache service to fetch the cert chain of the
// chip identified by chipId running firmware identified by reportedTCB. These attributes
// are retrived from the attestation report.
// Returns the cert chain as a bytes array, the TCBM from the local THIM cert cache is as a string
// (only in the case of a local THIM endpoint), and any errors encountered
func (certFetcher CertFetcher) retrieveCertChain(chipID string, reportedTCB uint64) ([]byte, uint64, error) {
	// HTTP GET request to cert cache service
	var uri string
	var thimTcbm uint64
	var thimCerts common.THIMCerts

	reportedTCBBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(reportedTCBBytes, reportedTCB)

	if certFetcher.Endpoint != "" {
		switch certFetcher.EndpointType {
		case "AMD":
			// AMD cert cache endpoint returns the VCEK certificate in DER format
			uri = fmt.Sprintf(AmdVCEKRequestURITemplate, certFetcher.Endpoint, certFetcher.TEEType, chipID, reportedTCBBytes[UcodeSplTcbmByteIndex], reportedTCBBytes[SnpSplTcbmByteIndex], reportedTCBBytes[TeeSplTcbmByteIndex], reportedTCBBytes[BlSplTcbmByteIndex])
			httpResponse, err := common.HTTPGetRequest(uri, false)
			if err != nil {
				return nil, reportedTCB, errors.Wrapf(err, "AMD certcache http get request failed")
			}
			derBytes, err := common.HTTPResponseBody(httpResponse)
			if err != nil {
				return nil, reportedTCB, err
			}
			// encode the VCEK cert in PEM format
			vcekPEMBytes := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: derBytes})

			// now retrieve the cert chain
			uri = fmt.Sprintf(AmdCertChainRequestURITemplate, certFetcher.Endpoint, certFetcher.TEEType)
			httpResponse, err = common.HTTPGetRequest(uri, false)
			if err != nil {
				return nil, reportedTCB, errors.Wrapf(err, "AMD certcache http get request failed")
			}
			certChainPEMBytes, err := common.HTTPResponseBody(httpResponse)
			if err != nil {
				return nil, reportedTCB, errors.Wrapf(err, "pulling AMD certchain response from get request failed")
			}

			// constuct full chain by appending the VCEK cert to the cert chain
			fullCertChain := append(vcekPEMBytes, certChainPEMBytes[:]...)

			return fullCertChain, reportedTCB, nil
		case "LocalTHIM":
			uri = fmt.Sprintf(LocalTHIMUriTemplate, certFetcher.Endpoint)
			// local THIM cert cache endpoint returns THIM Certs object
			httpResponse, err := common.HTTPGetRequest(uri, false)
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "certcache http get request failed")
			}
			THIMCertsBytes, err := common.HTTPResponseBody(httpResponse)
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "pulling certchain response from get request failed")
			}

			thimCerts, thimTcbm, err := thimCerts.GetLocalCerts(string(THIMCertsBytes))
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "certcache failed to get local certs")
			}

			return []byte(thimCerts), thimTcbm, nil
		case "AzCache":
			uri = fmt.Sprintf(AzureCertCacheRequestURITemplate, certFetcher.Endpoint, certFetcher.TEEType, chipID, strconv.FormatUint(reportedTCB, 16), certFetcher.APIVersion)
			httpResponse, err := common.HTTPGetRequest(uri, false)
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "AzCache http get request failed")
			}
			certChain, err := common.HTTPResponseBody(httpResponse)
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "pulling certchain response from AzCache get request failed")
			}
			thimTcbm, err = ParseVCEK(certChain)
			if err != nil {
				return nil, thimTcbm, errors.Wrapf(err, "AzCache failed to parse VCEK from cert chain")
			}
			return certChain, thimTcbm, nil
		default:
			return nil, thimTcbm, errors.Errorf("invalid endpoint type: %s", certFetcher.EndpointType)
		}
	} else {
		return nil, thimTcbm, errors.Errorf("failed to retrieve cert chain: certificate endpoint not set")
	}
}

func (certFetcher CertFetcher) GetCertChain(chipID string, reportedTCB uint64) ([]byte, uint64, error) {
	return certFetcher.retrieveCertChain(chipID, reportedTCB)
}
