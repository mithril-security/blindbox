// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package common

import (
	"bytes"
	"io/ioutil"
	"net/http"

	"github.com/pkg/errors"
)

func httpClientDoRequest(req *http.Request) (*http.Response, error) {
	httpClientDoWrapper := func() (interface{}, error) {
		client := &http.Client{}
		return client.Do(req)
	}

	resp, err := httpClientDoWrapper()

	if err != nil {
		return nil, errors.Wrapf(err, "HTTP GET failed")
	}

	return resp.(*http.Response), nil
}

func HTTPGetRequest(uri string, metadata bool) (*http.Response, error) {
	req, err := http.NewRequest("GET", uri, nil)
	if err != nil {
		return nil, errors.Wrapf(err, "http get request creation failed")
	}

	if metadata {
		req.Header.Add("Metadata", "true")
	}

	return httpClientDoRequest(req)
}

func HTTPPRequest(httpType string, uri string, jsonData []byte, authorizationToken string) (*http.Response, error) {
	if httpType != "POST" && httpType != "PUT" {
		return nil, errors.Errorf("invalid http request")
	}

	req, err := http.NewRequest(httpType, uri, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, errors.Wrapf(err, "http post request creation failed")
	}

	req.Header.Set("Content-Type", "application/json")
	if authorizationToken != "" {
		req.Header.Add("Authorization", "Bearer "+authorizationToken)
	}

	return httpClientDoRequest(req)
}

func HTTPResponseBody(httpResponse *http.Response) ([]byte, error) {
	if httpResponse.Status != "200 OK" && httpResponse.Status != "200 " {
		return nil, errors.Errorf("http response status equal to %s", httpResponse.Status)
	}

	// Pull out response body
	defer httpResponse.Body.Close()
	httpResponseBodyBytes, err := ioutil.ReadAll(httpResponse.Body)
	if err != nil {
		return nil, errors.Wrapf(err, "reading http response body failed")
	}

	return httpResponseBodyBytes, nil
}
