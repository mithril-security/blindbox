package bootstrapper

import (
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"os/exec"

	getter "github.com/hashicorp/go-getter"
	"github.com/google/uuid"
)

type Artifact struct {
	URL         string
	Hash        string
	InstallPath string
	Extract     bool
	Run         [][]string
}

type Artifacts []Artifact

const containerdService = `# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
#uncomment to enable the experimental sbservice (sandboxed) version of containerd/cri integration
#Environment="ENABLE_CRI_SANDBOXES=sandboxed"
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5
# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity
# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target`

const kubeletService = `[Unit]
Description=kubelet: The Kubernetes Node Agent
Documentation=https://kubernetes.io/docs/home/
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/usr/local/bin/kubelet
Restart=always
StartLimitInterval=0
RestartSec=10

[Install]
WantedBy=multi-user.target`

const kubeadmConf = `# Note: This dropin only works with kubeadm and kubelet v1.11+
[Service]
Environment="KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf"
Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml"
# This is a file that "kubeadm init" and "kubeadm join" generates at runtime, populating the KUBELET_KUBEADM_ARGS variable dynamically
EnvironmentFile=-/var/lib/kubelet/kubeadm-flags.env
# This is a file that the user can use for overrides of the kubelet args as a last resort. Preferably, the user should use
# the .NodeRegistration.KubeletExtraArgs object in the configuration files instead. KUBELET_EXTRA_ARGS should be sourced from this file.
EnvironmentFile=-/etc/default/kubelet
ExecStart=
ExecStart=/usr/local/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS`

var K8sArtifacts Artifacts = Artifacts {
	{
		URL:         "https://github.com/containerd/containerd/releases/download/v1.7.2/containerd-1.7.2-linux-amd64.tar.gz",
		Hash:        "sha256:2755c70152ab40856510b4549c2dd530e15f5355eb7bf82868e813c9380e22a7",
		InstallPath: "/usr/local",
		Extract:     true,
		Run:         [][]string{[]string{"echo", fmt.Sprintf("\"%s\"", containerdService), ">", "/usr/local/lib/systemd/system/containerd.service"},[]string{"systemctl", "daemon-reload"},[]string{"systemctl", "enable", "--now", "containerd"}},
	},
	{
		URL:         "https://github.com/opencontainers/runc/releases/download/v1.1.7/runc.amd64",
		Hash:        "sha256:c3aadb419e5872af49504b6de894055251d2e685fddddb981a79703e7f895cbd",
		InstallPath: "/usr/local/sbin/runc",
		Extract:     false,
		Run:         [][]string{},
	},
	{
		URL:         "https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz",
		Hash:        "sha256:754a71ed60a4bd08726c3af705a7d55ee3df03122b12e389fdba4bea35d7dd7e",
		InstallPath: "/opt/cni/bin",
		Extract:     true,
		Run:         [][]string{},
	},
	{
		URL:         "https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.27.0/crictl-v1.27.0-linux-amd64.tar.gz",
		Hash:        "sha256:d335d6e16c309fbc3ff1a29a7e49bb253b5c9b4b030990bf7c6b48687f985cee",
		InstallPath: "/usr/local/bin",
		Extract:     true,
		Run:         [][]string{},
	},
	{
		URL:         "https://dl.k8s.io/release/v1.27.2/bin/linux/amd64/kubeadm",
		Hash:        "sha256:95c4bfb7929900506a42de4d92280f06efe6b47e0a32cbc1f5a1ed737592977a",
		InstallPath: "/usr/local/bin/kubeadm",
		Extract:     false,
		Run:         [][]string{},
	},
	{
		URL:         "https://dl.k8s.io/release/v1.27.2/bin/linux/amd64/kubelet",
		Hash:        "sha256:a0d12afcab3b2836de4a427558d067bebdff040e9b306b0512c93d9d2a066579",
		InstallPath: "/usr/local/bin/kubelet",
		Extract:     false,
		Run:         [][]string{
			[]string{"echo", fmt.Sprintf("\"%s\"", kubeletService), "|", "tee", "/etc/systemd/system/kubelet.service"},
			[]string{"mkdir", "-p", "/etc/systemd/system/kubelet.service.d"},
			[]string{"echo", fmt.Sprintf("\"%s\"", kubeadmConf), "|", "tee", "/etc/systemd/system/kubelet.service.d/10-kubeadm.conf"},
			[]string{"systemctl", "enable", "--now", "kubelet"},
		},
	},
	{
		URL:         "https://dl.k8s.io/release/v1.27.2/bin/linux/amd64/kubectl",
		Hash:        "sha256:4f38ee903f35b300d3b005a9c6bfb9a46a57f92e89ae602ef9c129b91dc6c5a5",
		InstallPath: "/usr/local/bin/kubectl",
		Extract:     false,
		Run:         [][]string{},
	},
}

func (as *Artifacts) InstallAndVerify() error {
	for _, a := range *as {
		if err := a.InstallAndVerify(); err != nil {
			return err
		}
		for _, args := range a.Run {
			tail := args[0]
			if err := exec.Command(tail, args[1:]...).Run(); err != nil {
				return err
			}
		}
	}

	return nil
}

func (a *Artifact) InstallAndVerify() error {
	tmpPath := fmt.Sprintf("/tmp/%s", uuid.New())
	if err := getter.GetFile(tmpPath, a.URL); err != nil {
		return err
	}
	// client := getter.ClientFromContext(ctx)
	// _, err := client.Get(ctx, &getter.Request {
	// 	Src: a.URL,
	// 	Dst: tmpPath,
	// })
	// if err != nil {
	// 	return err
	// }

	tmpfile, err := os.OpenFile(tmpPath, os.O_RDONLY, 0)
	if err != nil {
		return fmt.Errorf("reading tmp file %q: %w", tmpPath, err)
	}

	sha := sha256.New()
	if _, err := io.Copy(sha, tmpfile); err != nil {
		return fmt.Errorf("cannot hash file %q: %w", tmpPath, err)
	}
	tmpfile.Close()
	calculatedHash := fmt.Sprintf("sha256:%x", sha.Sum(nil))
	if calculatedHash != a.Hash {
		return fmt.Errorf("hash of file %q %s does not match expected hash %s", a.InstallPath, calculatedHash, a.Hash)
	}

	if a.Extract {
		tarballPath := fmt.Sprintf("%s_extracted", tmpPath)
		UnGzip(tmpPath, tarballPath)
		Untar(tarballPath, a.InstallPath)
	} else {
		installExecutable(tmpPath, a.InstallPath)
	}
	
	return nil
}

func installExecutable(src string, dst string) error {
	srcfile, err := os.OpenFile(src, os.O_RDONLY, 0)
	if err != nil {
		return fmt.Errorf("reading tmp file %q: %w", src, err)
	}
	defer srcfile.Close()

	dstfile, err := os.OpenFile(dst, os.O_WRONLY|os.O_TRUNC|os.O_CREATE, 0544)
	if err != nil {
		return fmt.Errorf("installing file %q: %w", dst, err)
	}
	defer dstfile.Close()

	if _, err := io.Copy(dstfile, srcfile); err != nil {
		return fmt.Errorf("installing file %q: %w", dst, err)
	}

	return nil
}
