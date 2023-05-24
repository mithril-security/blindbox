# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

CFLAGS:=-O2 -Wall
LDFLAGS:=-static -s # strip C binaries

all: bin/get-snp-report

bin/get-snp-report: get-snp-report.o get-snp-report5.o get-snp-report6.o helpers.o
	@mkdir -p bin
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(CPPFLAGS) -c -o $@ $<

clean:
	find -name '*.o' -print0 | xargs -0 -r rm
	rm -rf bin out
