# FIPS APK repository

Signed Wolfi packages for the OpenSSL FIPS Provider 3.1.2, the FIPS 140-3 validated module with
[CMVP certificate #4985](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4985).
They are built with [melange](https://github.com/chainguard-dev/melange) for `x86_64` and `aarch64`
and published at `https://taha2samy-3.github.io/node/apk`.

| Package | Contents |
| :--- | :--- |
| `openssl-provider-fips-3.1.2` | `/usr/lib/ossl-modules/fips.so` and `/etc/ssl/fipsmodule.cnf` with the module's integrity MAC |
| `openssl-config-fipshardened` | `/etc/ssl/openssl.cnf` that loads only the FIPS and base providers with `default_properties = fips=yes` |

## Install

```sh
wget -O /etc/apk/keys/taha2samy-3-fips.rsa.pub \
  https://taha2samy-3.github.io/node/apk/taha2samy-3-fips.rsa.pub
echo https://taha2samy-3.github.io/node/apk >> /etc/apk/repositories
apk add openssl-config-fipshardened
```

`openssl-config-fipshardened` pulls in the provider and takes over `/etc/ssl/openssl.cnf` from
`libcrypto3`, so every program that uses the system OpenSSL runs in the approved mode. Install only
`openssl-provider-fips-3.1.2` to load the module through your own configuration instead.

In a Dockerfile:

```dockerfile
FROM cgr.dev/chainguard/wolfi-base
ADD https://taha2samy-3.github.io/node/apk/taha2samy-3-fips.rsa.pub /etc/apk/keys/
RUN echo https://taha2samy-3.github.io/node/apk >> /etc/apk/repositories && \
    apk add --no-cache openssl openssl-config-fipshardened && \
    openssl list -providers
```

## How the module is built

The build in `openssl-provider-fips-3.1.2.yaml` follows section 11.1 of the
[security policy](https://csrc.nist.gov/CSRC/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp4985.pdf):

1. The source is the `openssl-3.1.2.tar.gz` named in the policy, checked against its SHA-256
   `a0ce69b8b97ea6a35b96875235aa453b966ba3cba8af2de23657d8b6767d6539`.
2. `./Configure enable-fips`, `make` and `make install_fips`, with no other options and no patches.
3. `fipsmodule.cnf` is written only by the module's own `openssl fipsinstall -pedantic`, and
   checked with `fipsinstall -verify`. Nothing else edits it, and `fips.so` is never stripped.
4. With `-self_test_onload`, the 3.1.2 default, the known-answer self tests and the integrity check
   run every time the module loads, so they run on each machine the package is installed on.

The package tests load the module through Wolfi's `libcrypto3`, check that MD5 is refused, and check
that a tampered integrity MAC stops the module from loading.

## What the certificate covers

The certificate covers the module only on its tested operational environments. Those are Ubuntu
22.04, Debian 11, FreeBSD 13.1, Windows 10 and macOS 11 on Intel x86_64, and macOS 11 on Apple M1.
No environment is vendor affirmed.

Running the module on Wolfi is a port to an untested operational environment under FIPS 140-3
Implementation Guidance 2.3.A. The CMVP makes no statement about it, and the operator affirms that
the module is used unchanged. That applies to `x86_64`, and more strongly to `aarch64`, because Linux
on ARM is not among the tested environments at all.

## Maintenance

- Packages are immutable once published. A change needs a new `epoch` in the melange file.
- The module version only changes when NIST lists a new certificate. The weekly
  certificate watch (`.github/scripts/cmvp_watch.py`) opens an issue when that happens.
- The repository key lives in the `MELANGE_SIGNING_KEY` secret. Its public half is
  `keys/taha2samy-3-fips.rsa.pub`. Replacing the key means every user downloads the new public key.

Build locally, which compiles OpenSSL and needs a few GB of RAM:

```sh
docker run --rm --privileged -v "$PWD":/work -w /work cgr.dev/chainguard/melange build \
  melange/openssl-provider-fips-3.1.2.yaml --arch x86_64 \
  --source-dir melange/openssl-provider-fips-3.1.2 --signing-key melange.rsa
```
