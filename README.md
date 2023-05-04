# CLI

```sh
$ ls
Dockerfile
main.js
package.json
$ docker build -t myapp:v1 .
...

# Create a blindbox configuration
$ blindbox init --platform azure-sev
$ ls
blindbox.tf # <- terraform file, editable by the user
blindbox.yml
$ cat blindbox.yml
ip-access-whitelist:
  - 33.33.33.129
proxy-setting: "idk"

$ blindbox build -t myimage-blindbox:v1 --source-image myapp:v1
# runs the docker build process
# tags the new myimage-blindbox image

$ blindbox deploy
# blindbox deploy would be a litteral alias to the command `terraform apply`
# we don't need to wrapper over it

```
