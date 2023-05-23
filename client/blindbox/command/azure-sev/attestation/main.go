// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package main

import (
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	"ACI_Attest/attest"
	"ACI_Attest/common"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

var (
	ServerCertState       attest.CertState
	EncodedUvmInformation common.UvmInformation
	ready                 bool
)

type AzureInformation struct {
	// Endpoint of the certificate cache service from which
	// the certificate chain endorsing hardware attestations
	// can be retrieved. This is optional only when the container
	// will expose attest/maa and key/release APIs.
	CertFetcher attest.CertFetcher `json:"certcache,omitempty"`
}

type MAAAttestData struct {
	// MAA endpoint which authors the MAA token
	MAAEndpoint string `json:"maa_endpoint" binding:"required"`
	// Base64 encoded representation of runtime data to be encoded
	// as runtime claim in the MAA token
	RuntimeData string `json:"runtime_data" binding:"required"`
}

type RawAttestData struct {
	// Base64 encoded representation of runtime data whose hash digest
	// will be encoded as ReportData in the hardware attestation repport
	RuntimeData string `json:"runtime_data" binding:"required"`
}

func usage() {
	fmt.Printf("Usage of %s:\n", os.Args[0])
	flag.PrintDefaults()
}

func getStatus(c *gin.Context) {
	if ready {
		c.JSON(http.StatusOK, gin.H{"message": "Status OK"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Status NOT OK"})
}

// postRawAttest retrieves a hardware attestation report signed by the
// Platform Security Processor and which encodes the hash digest of
// the request's RuntimeData in the attestation's ReportData
//
// - RuntimeData is expected to be a base64-standard-encoded string
func postRawAttest(c *gin.Context) {
	var attestData RawAttestData

	// Call BindJSON to bind the received JSON to AttestData
	if err := c.ShouldBindJSON(&attestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": errors.Wrapf(err, "invalid request format").Error()})
		return
	}

	// base64 decode the incoming encoded security policy
	inittimeDataBytes, err := base64.StdEncoding.DecodeString(EncodedUvmInformation.EncodedSecurityPolicy)

	if err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": errors.Wrap(err, "decoding policy from Base64 format failed").Error()})
		return
	}

	// standard base64 decode the incoming runtime data
	runtimeDataBytes, err := base64.StdEncoding.DecodeString(attestData.RuntimeData)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": errors.Wrapf(err, "decoding base64-encoded runtime data of request failed").Error()})
		return
	}

	rawReport, err := attest.RawAttest(inittimeDataBytes, runtimeDataBytes)
	if err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
	}

	c.JSON(http.StatusOK, gin.H{"report": rawReport})
}

// postMAAAttest retrieves an attestation token issued by Microsoft Azure Attestation
// service which encodes the request's RuntimeData as a runtime claim
//
//   - RuntimeData is expected to be a base64-standard-encoded string
//   - MAAEndpoint is the uri to the Microsoft Azure Attestation service endpoint which
//     will author and sign the attestation token
func postMAAAttest(c *gin.Context) {
	var attestData MAAAttestData

	// call BindJSON to bind the received JSON to AttestData
	if err := c.ShouldBindJSON(&attestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": errors.Wrapf(err, "invalid request format").Error()})
		return
	}

	// base64 decode the incoming runtime data
	runtimeDataBytes, err := base64.StdEncoding.DecodeString(attestData.RuntimeData)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": errors.Wrapf(err, "decoding base64-encoded runtime data of request failed").Error()})
		return
	}

	maa := attest.MAA{
		Endpoint:   attestData.MAAEndpoint,
		TEEType:    "SevSnpVM",
		APIVersion: "api-version=2020-10-01",
	}

	if err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
	}

	maaToken, err := ServerCertState.Attest(maa, runtimeDataBytes, EncodedUvmInformation)
	if err != nil {
		c.JSON(http.StatusForbidden, gin.H{"error": err.Error()})
	}

	c.JSON(http.StatusOK, gin.H{"token": maaToken})
}


func setupServer(certState attest.CertState) *gin.Engine {
	ServerCertState = certState

	certString := EncodedUvmInformation.InitialCerts.VcekCert + EncodedUvmInformation.InitialCerts.CertificateChain
	r := gin.Default()

	r.GET("/status", getStatus)
	r.POST("/attest/raw", postRawAttest)

	// the implementation of attest/maa and key/release APIs call MAA service
	// to retrieve a MAA token. The MAA API requires that the request carries
	// the certificate chain endording the signing key of the hardware attestation.
	// Hence, these APIs are exposed only if the platform certificate information
	// has been provided at startup time.
	if certState.CertFetcher.Endpoint != "" || certString != "" {
		r.POST("/attest/maa", postMAAAttest)
	}

	ready = true

	return r
}

func main() {

	azureInfoBase64string := flag.String("base64", "", "optional base64-encoded json string with azure information")
	logLevel := flag.String("loglevel", "debug", "Logging Level: trace, debug, info, warning, error, fatal, panic.")
	logFile := flag.String("logfile", "", "Logging Target: An optional file name/path. Omit for console output.")
	port := flag.String("port", "8080", "Port on which to listen")

	// WARNING!!!
	// If the security policy does not control the arguments to this process then
	// this hostname could be set to 0.0.0.0 (an external interface) rather than 127.0.0.1 (visible only
	// witin the container group/pod)and so expose the attestation outside of the secure uvm

	// Leaving this line here, as a comment, to aid debugging.
	// hostname := flag.String("hostname", "localhost", "address on which to listen (dangerous)")
	hostname := "0.0.0.0"

	flag.Usage = usage

	flag.Parse()

	if *logFile != "" {
		// If the file doesn't exist, create it. If it exists, append to it.
		file, err := os.OpenFile(*logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
		if err != nil {
			logrus.Fatal(err)
		}
		defer file.Close()
		logrus.SetOutput(file)
	}

	level, err := logrus.ParseLevel(*logLevel)
	if err != nil {
		logrus.Fatal(err)
	}
	logrus.SetLevel(level)
	logrus.SetFormatter(&logrus.TextFormatter{FullTimestamp: false, DisableQuote: true, DisableTimestamp: true})

	logrus.Infof("Starting %s...", os.Args[0])

	logrus.Infof("Args:")
	logrus.Debugf("   Log Level:     %s", *logLevel)
	logrus.Debugf("   Log File:      %s", *logFile)
	logrus.Debugf("   Port:          %s", *port)
	logrus.Debugf("   Hostname:      %s", hostname)
	logrus.Debugf("   azure info:    %s", *azureInfoBase64string)

	//set environment variable pointing to ACI's certs
	files, err := os.ReadDir("/")
	for _, file := range files {
		if strings.HasPrefix(file.Name(),"security-context") {
		os.Setenv("UVM_SECURITY_CONTEXT_DIR","/"+file.Name())
		}
	}

	EncodedUvmInformation, err = common.GetUvmInformation() // from the env.
	if err != nil {
		logrus.Fatalf("Failed to extract UVM_* environment variables: %s", err.Error())
	}

	info := AzureInformation{}

	// Decode base64 attestation information only if it s not empty
	if *azureInfoBase64string != "" {
		bytes, err := base64.StdEncoding.DecodeString(*azureInfoBase64string)
		if err != nil {
			logrus.Fatalf("Failed to decode base64: %s", err.Error())
		}

		err = json.Unmarshal(bytes, &info)
		if err != nil {
			logrus.Fatalf("Failed to unmarshal: %s", err.Error())
		}
	}

	// See above comment about hostname and risk of breaking confidentiality
	url := hostname + ":" + *port

	var tcbm string
	tcbm = EncodedUvmInformation.InitialCerts.Tcbm

	thimTcbm, err := strconv.ParseUint(tcbm, 16, 64)
	if err != nil {
		logrus.Fatal("Unable to convert intial TCBM to a uint64")
	}

	certState := attest.CertState{
		CertFetcher: info.CertFetcher,
		Tcbm:        thimTcbm,
	}

	setupServer(certState).Run(url)
}
