// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package common

import (
	"encoding/base64"
	"encoding/json"
	_ "io/ioutil"
	"strconv"

	"os"
	"path/filepath"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

// Set to true to regenerate test files at every request.
// Also useful to debug the various steps, especially encoding
// to the correct base64url encoding.

const GenerateTestData = false

// format of the json provided to the UVM by hcsshim. Comes from the THIM endpoint
// and is a base64 encoded json string
type THIMCerts struct {
	VcekCert         string `json:"vcekCert"`
	Tcbm             string `json:"tcbm"`
	CertificateChain string `json:"certificateChain"`
	CacheControl     string `json:"cacheControl"`
}

func (thimCerts *THIMCerts) GetLocalCerts(encodedHostCertsFromTHIM string) (string, uint64, error) {
	var thimTcbm uint64
	hostCertsFromTHIM, err := base64.StdEncoding.DecodeString(encodedHostCertsFromTHIM)
	if err != nil {
		return "", thimTcbm, errors.Wrapf(err, "base64 decoding platform certs failed")
	}

	//var certsFromTHIM THIMCerts
	err = json.Unmarshal(hostCertsFromTHIM, &thimCerts)
	if err != nil {
		return "", thimTcbm, errors.Wrapf(err, "json unmarshal platform certs failed")
	}

	certsString := thimCerts.VcekCert + thimCerts.CertificateChain

	logrus.Debugf("certsFromTHIM:\n\n%s\n\n", certsString)
	logrus.Debugf("thimTcbm: %s\n\n", thimCerts.Tcbm)

	thimTcbm, err = strconv.ParseUint(thimCerts.Tcbm, 16, 64)
	if err != nil {
		return "", thimTcbm, errors.Wrap(err, "Unable to convert TCBM from THIM certificates to a uint64")
	}

	return certsString, thimTcbm, nil
}

type UvmInformation struct {
	EncodedSecurityPolicy   string    // customer security policy
	InitialCerts            THIMCerts // platform certificates for the actual physical host
	EncodedUvmReferenceInfo string    // endorsements for the particular UVM image
}

// Late in Public Preview, we made a change to pass the UVM information
// via files instead of environment variables.
// This code detects which method is being used and calls the appropriate
// function to get the UVM information.

// The environment variable scheme will go away by "General Availability"
// but we handle both to decouple this code and the hcsshim/gcs code.

// Matching PR https://github.com/microsoft/hcsshim/pull/1708

func GetUvmInformation() (UvmInformation, error) {
	securityContextDir := os.Getenv("UVM_SECURITY_CONTEXT_DIR")
	if securityContextDir != "" {
		return GetUvmInformationFromFiles()
	} else {
		return GetUvmInformationFromEnv()
	}
}

func GetUvmInformationFromEnv() (UvmInformation, error) {
	var encodedUvmInformation UvmInformation

	encodedHostCertsFromTHIM := os.Getenv("UVM_HOST_AMD_CERTIFICATE")

	if encodedHostCertsFromTHIM != "" {
		_, _, err := encodedUvmInformation.InitialCerts.GetLocalCerts(encodedHostCertsFromTHIM)
		if err != nil {
			return encodedUvmInformation, err
		}
	}
	encodedUvmInformation.EncodedSecurityPolicy = os.Getenv("UVM_SECURITY_POLICY")
	encodedUvmInformation.EncodedUvmReferenceInfo = os.Getenv("UVM_REFERENCE_INFO")

	return encodedUvmInformation, nil
}

// From hcsshim pkg/securitypolicy/securitypolicy.go

const (
	SecurityContextDirTemplate = "security-context-*"
	PolicyFilename             = "security-policy-base64"
	HostAMDCertFilename        = "host-amd-cert-base64"
	ReferenceInfoFilename      = "reference-info-base64"
)

func readSecurityContextFile(dir string, filename string) (string, error) {
	targetFilename := filepath.Join(dir, filename)
	blob, err := os.ReadFile(targetFilename)
	if err != nil {
		return "", err
	}
	return string(blob), nil
}

func GetUvmInformationFromFiles() (UvmInformation, error) {
	var encodedUvmInformation UvmInformation

	securityContextDir := os.Getenv("UVM_SECURITY_CONTEXT_DIR")
	if securityContextDir == "" {
		return encodedUvmInformation, errors.New("UVM_SECURITY_CONTEXT_DIR not set")
	}

	encodedHostCertsFromTHIM, err := readSecurityContextFile(securityContextDir, HostAMDCertFilename)
	if err != nil {
		return encodedUvmInformation, errors.Wrapf(err, "reading host amd cert failed")
	}

	if encodedHostCertsFromTHIM != "" {
		_, _, err := encodedUvmInformation.InitialCerts.GetLocalCerts(encodedHostCertsFromTHIM)
		if err != nil {
			return encodedUvmInformation, err
		}
	}

	encodedUvmInformation.EncodedSecurityPolicy, err = readSecurityContextFile(securityContextDir, PolicyFilename)
	if err != nil {
		return encodedUvmInformation, errors.Wrapf(err, "reading security policy failed")
	}

	encodedUvmInformation.EncodedUvmReferenceInfo, err = readSecurityContextFile(securityContextDir, ReferenceInfoFilename)
	if err != nil {
		return encodedUvmInformation, errors.Wrapf(err, "reading uvm reference info failed")
	}

	return encodedUvmInformation, nil
}
