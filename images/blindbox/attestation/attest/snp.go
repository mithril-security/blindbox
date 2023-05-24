// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package attest

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"

	_ "io/ioutil"
	"os/exec"

	"github.com/pkg/errors"
	_ "github.com/sirupsen/logrus"
)

const (
	snpReportSize = 1184
)

type SNPAttestationReport struct {
	// version no. of this attestation report. Set to 1 for this specification.
	Version uint32 `json:"version"`
	// The guest SVN
	GuestSvn uint32 `json:"guest_svn"`
	// see table 8 - various settings
	Policy uint64 `json:"policy"`
	// as provided at launch    hex string of a 16-byte integer
	FamilyID string `json:"family_id"`
	// as provided at launch 	hex string of a 16-byte integer
	ImageID string `json:"image_id"`
	// the request VMPL for the attestation report
	VMPL          uint32 `json:"vmpl"`
	SignatureAlgo uint32 `json:"signature_algo"`
	// The install version of the firmware
	PlatformVersion uint64 `json:"platform_version"`
	// information about the platform see table 22
	PlatformInfo uint64 `json:"platform_info"`
	// 31 bits of reserved, must be zero, bottom bit indicates that the digest of the author key is present in AUTHOR_KEY_DIGEST. Set to the value of GCTX.AuthorKeyEn.
	AuthorKeyEn uint32 `json:"author_key_en"`
	// must be zero
	Reserved1 uint32 `json:"reserved1"`
	// Guest provided data.	64-byte
	ReportData string `json:"report_data"`
	// measurement calculated at launch 48-byte
	Measurement string `json:"measurement"`
	// data provided by the hypervisor at launch 32-byte
	HostData string `json:"host_data"`
	// SHA-384 digest of the ID public key that signed the ID block provided in SNP_LAUNCH_FINISH 48-byte
	IDKeyDigest string `json:"id_key_digest"`
	// SHA-384 digest of the Author public key that certified the ID key, if provided in SNP_LAUNCH_FINISH. Zeros if author_key_en is 1 (sounds backwards to me). 48-byte
	AuthorKeyDigest string `json:"author_key_digest"`
	// Report ID of this guest. 32-byte
	ReportID string `json:"report_id"`
	// Report ID of this guest's mmigration agent. 32-byte
	ReportIDMA string `json:"report_id_ma"`
	// Reported TCB version used to derive the VCEK that signed this report
	ReportedTCB uint64 `json:"reported_tcb"`
	// reserved 24-byte
	Reserved2 string `json:"reserved2"`
	// Identifier unique to the chip 64-byte
	ChipID string `json:"chip_id"`
	// The current commited SVN of the firware (version 2 report feature)
	CommittedSvn uint64 `json:"committed_svn"`
	// The current commited version of the firware
	CommittedVersion uint64 `json:"committed_version"`
	// The SVN that this guest was launched or migrated at
	LaunchSvn uint64 `json:"launch_svn"`
	// reserved 168-byte
	Reserved3 string `json:"reserved3"`
	// Signature of this attestation report. See table 23. 512-byte
	Signature string `json:"signature"`
}

func (r *SNPAttestationReport) DeserializeReport(report []uint8) error {

	if len(report) != snpReportSize {
		return errors.Errorf("invalid snp report size")
	}

	r.Version = binary.LittleEndian.Uint32(report[0:4])
	r.GuestSvn = binary.LittleEndian.Uint32(report[4:8])
	r.Policy = binary.LittleEndian.Uint64(report[8:16])
	r.FamilyID = hex.EncodeToString(report[16:32])
	r.ImageID = hex.EncodeToString(report[32:48])
	r.VMPL = binary.LittleEndian.Uint32(report[48:52])
	r.SignatureAlgo = binary.LittleEndian.Uint32(report[52:56])
	r.PlatformVersion = binary.LittleEndian.Uint64(report[56:64])
	r.PlatformInfo = binary.LittleEndian.Uint64(report[64:72])
	r.AuthorKeyEn = binary.LittleEndian.Uint32(report[72:76])
	r.Reserved1 = binary.LittleEndian.Uint32(report[76:80])
	r.ReportData = hex.EncodeToString(report[80:144])
	r.Measurement = hex.EncodeToString(report[144:192])
	r.HostData = hex.EncodeToString(report[192:224])
	r.IDKeyDigest = hex.EncodeToString(report[224:272])
	r.AuthorKeyDigest = hex.EncodeToString(report[272:320])
	r.ReportID = hex.EncodeToString(report[320:352])
	r.ReportIDMA = hex.EncodeToString(report[352:384])
	r.ReportedTCB = binary.LittleEndian.Uint64(report[384:392])
	r.Reserved2 = hex.EncodeToString(report[392:416])
	r.ChipID = hex.EncodeToString(report[416:480])
	r.CommittedSvn = binary.LittleEndian.Uint64(report[480:488])
	r.CommittedVersion = binary.LittleEndian.Uint64(report[488:496])
	r.LaunchSvn = binary.LittleEndian.Uint64(report[496:504])
	r.Reserved3 = hex.EncodeToString(report[504:672])
	r.Signature = hex.EncodeToString(report[672:1184])

	return nil
}

func (r *SNPAttestationReport) SerializeReport() (report []uint8, err error) {
	report = make([]uint8, snpReportSize) // size of struct is 1184 bytes

	binary.LittleEndian.PutUint32(report[0:4], r.Version)
	binary.LittleEndian.PutUint32(report[4:8], r.GuestSvn)
	binary.LittleEndian.PutUint64(report[8:16], r.Policy)

	familyIDByteArray, err := hex.DecodeString(r.FamilyID)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.FamilyID failed")
	}
	for index, b := range familyIDByteArray {
		report[index+16] = b
	}

	imageIDByteArray, err := hex.DecodeString(r.ImageID)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.ImageID failed")
	}
	for index, b := range imageIDByteArray {
		report[index+32] = b
	}

	binary.LittleEndian.PutUint32(report[48:52], r.VMPL)
	binary.LittleEndian.PutUint32(report[52:56], r.SignatureAlgo)
	binary.LittleEndian.PutUint64(report[56:64], r.PlatformVersion)
	binary.LittleEndian.PutUint64(report[64:72], r.PlatformInfo)
	binary.LittleEndian.PutUint32(report[72:76], r.AuthorKeyEn)
	binary.LittleEndian.PutUint32(report[76:80], r.Reserved1)

	reportDataByteArray, err := hex.DecodeString(r.ReportData)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.ReportData failed")
	}
	for index, b := range reportDataByteArray {
		report[index+80] = b
	}

	measurementByteArray, err := hex.DecodeString(r.Measurement)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.Measurement failed")
	}
	for index, b := range measurementByteArray {
		report[index+144] = b
	}

	hostDataByteArray, err := hex.DecodeString(r.HostData)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.HostData failed")
	}
	for index, b := range hostDataByteArray {
		report[index+192] = b
	}

	IDKeyDigestByteArray, err := hex.DecodeString(r.IDKeyDigest)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.IDKeyDigest failed")
	}
	for index, b := range IDKeyDigestByteArray {
		report[index+224] = b
	}

	authorKeyDigestByteArray, err := hex.DecodeString(r.AuthorKeyDigest)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.AuthorKeyDigest failed")
	}
	for index, b := range authorKeyDigestByteArray {
		report[index+272] = b
	}

	reportIDByteArray, err := hex.DecodeString(r.ReportID)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.ReportID failed")
	}
	for index, b := range reportIDByteArray {
		report[index+320] = b
	}

	reportIDMAByteArray, err := hex.DecodeString(r.ReportIDMA)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.ReportIDMA failed")
	}
	for index, b := range reportIDMAByteArray {
		report[index+352] = b
	}

	binary.LittleEndian.PutUint64(report[384:392], r.ReportedTCB)

	reserved2ByteArray, err := hex.DecodeString(r.Reserved2)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.Reserved2 failed")
	}
	for index, b := range reserved2ByteArray {
		report[index+392] = b
	}

	chipIDByteArray, err := hex.DecodeString(r.ChipID)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.ChipID failed")
	}
	for index, b := range chipIDByteArray {
		report[index+416] = b
	}

	reserved3ByteArray, err := hex.DecodeString(r.Reserved3)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.Reserved3 failed")
	}
	for index, b := range reserved3ByteArray {
		report[index+480] = b
	}

	signatureByteArray, err := hex.DecodeString(r.Signature)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding r.Signature failed")
	}
	for index, b := range signatureByteArray {
		report[index+672] = b
	}

	return report, nil
}

// fetchSNPReport abstracts whether we fetch a real or a hardcoded snp
// report (for testing purposes)
func FetchSNPReport(real bool, keyBlob []byte, policyBlob []byte) ([]byte, error) {
	return fetchRealSNPReport(keyBlob)
}

// fetchRealSNPReport uses the get-snp-report tool to retrieve an attestation report from the PSP
// The attestation report retrieval request passes an arbiratry 64-byte block that will be
// reported as REPORT_DATA (reportBytes)
//
// The get-snp-report tool is compiled during preperation of the container rootfs. The binary is expected to
// be fount under /bin
func fetchRealSNPReport(keyBytes []byte) (reportBytes []byte, err error) {
	runtimeData := sha256.New()
	if keyBytes != nil {
		runtimeData.Write(keyBytes)
	}

	// the get-snp-report binary expects ReportData as the only command line attribute
	cmd := exec.Command("tools/get-snp-report/bin/get-snp-report", hex.EncodeToString(runtimeData.Sum(nil)))

	reportBytesString, err := cmd.Output()
	if err != nil {
		return nil, errors.Wrapf(err, "cmd.Run() for fetching snp report failed")
	}

	// the get-snp-report binary outputs the raw hexadecimal representation  of the report
	reportBytes = make([]byte, hex.DecodedLen(len(reportBytesString)))

	num, err := hex.Decode(reportBytes, reportBytesString)
	if err != nil {
		return nil, errors.Wrapf(err, "decoding output to hexstring failed")
	}

	if num != len(reportBytes) {
		return nil, errors.Wrapf(err, "decoding output not expected number of bytes")
	}

	return reportBytes, nil
}
