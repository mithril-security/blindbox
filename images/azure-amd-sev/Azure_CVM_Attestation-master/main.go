// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package main

import (
	"encoding/base64"
	"os/exec"
	"net/http"
	"github.com/pkg/errors"
	"github.com/gin-gonic/gin"
)

func main() {
	port := "8080"

	localhost := "localhost"
	hostname := &localhost

	url := *hostname + ":" + port

	setupServer(url)
}

func setupServer(url string) {
	server := gin.Default()
	server.POST("/attest/maa", PostMAAAttest)
	server.Run(url)
}

type MAAAttestData struct {
	// MAA endpoint which authors the MAA token
	MAAEndpoint string `json:"maa_endpoint" binding:"required"`
	// Base64 encoded representation of runtime data to be encoded
	// as runtime claim in the MAA token
	RuntimeData string `json:"runtime_data" binding:"required"`
}

func PostMAAAttest(c *gin.Context) {
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

	args := []string{"-n", string(runtimeDataBytes), "-a", attestData.MAAEndpoint, "-o", "token"}
	cmd := exec.Command("bin/AttestationClient", args...)

	maaToken, err := cmd.Output()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": errors.Wrapf(err, "cmd.Run() for fetching snp report and MAA token failed").Error()})
	}

	c.JSON(http.StatusOK, gin.H{"b64_maa_token": maaToken})
}